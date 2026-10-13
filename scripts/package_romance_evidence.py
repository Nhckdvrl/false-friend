#!/usr/bin/env python3
"""Archive the completed fourth cycle with source-text omissions and raw hashes."""
import argparse
from collections import Counter, defaultdict
import gzip
import hashlib
import json
from pathlib import Path
import shutil

try:
    from scripts.analyze_romance_cycle import summarize
    from scripts.analyze_doppelganger_diagnostics import bootstrap
except ModuleNotFoundError:
    from analyze_romance_cycle import summarize
    from analyze_doppelganger_diagnostics import bootstrap

MODELS=['llama8b','qwen14b','qwen32b','gemma12b']
RUN_NAMES=([f'2026-10-13-romance-{branch}-{m}' for branch in ['baseline','exploration'] for m in MODELS]
    +[f'2026-10-13-lexical-proposition-{m}' for m in MODELS]
    +[f'2026-10-13-gloss-binding-{m}' for m in MODELS[:2]]
    +[f'2026-10-13-scope-{m}' for m in ['qwen32b','gemma12b']])


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_rows(path):
    return [json.loads(x) for x in path.read_text().splitlines()]


def compact(row):
    row=dict(row)
    if row['task'] in {'romance_wic','independent_gloss'}:
        for key in ['C1','C2','prompt','rendered_prompt']:
            if key in row:
                row[key+'_sha256']=hashlib.sha256(row.pop(key).encode()).hexdigest()
    return row


def write_gzip(path, rows):
    # Deterministic gzip headers make the archive reproducible.
    with path.open('wb') as raw:
        with gzip.GzipFile(filename='',fileobj=raw,mode='wb',mtime=0) as handle:
            for row in rows:
                handle.write((json.dumps(row,ensure_ascii=False)+'\n').encode())


def family_metric(rows, key):
    values=defaultdict(list)
    for r in rows:
        cluster=("|".join(sorted((r['lexeme_family_id'],r['contrast_word'])))
                 if r.get('task')=='orthogonal_relation' else r['lexeme_family_id'])
        values[cluster].append(float(r[key]))
    return bootstrap(values)


def scope_pairs(decisions):
    index={r['trial_id']:r for r in decisions};pairs=[]
    for w in decisions:
        if w['condition']!='word':continue
        p=index[w['trial_id'].rsplit(':',1)[0]+':predicate']
        pairs.append(dict(trial_id=w['trial_id'],lexeme_family_id=w['lexeme_family_id'],split=w['split'],
            discordant_gold=w['gold_yes']!=p['gold_yes'],same_prediction=w['prediction']==p['prediction'],
            word_correct=w['correct'],predicate_correct=p['correct'],
            both_correct=w['correct'] and p['correct'],
            identical_prompt=w['negation_1']==w['negation_2']==0))
    assert len(pairs)==384
    return pairs


def package(root,destination):
    destination.mkdir(parents=True,exist_ok=False)
    manifest=dict(protocol='romance-relation-scope-cycle-archive-v1',
        source_repository='https://github.com/mrtva/false-friends-vs-cognates',
        source_sha='a87b73e387a6ef86d0cef7ffe703150905e75d7a',
        source_license_status='No LICENSE found; original corpus and source-containing prompts remain in ignored local runs.',
        policy='Keep model outputs, tokens, source IDs, raw hashes and code. Retain full authored prompts. Agent reviews are single nonblind reviews.',
        analysis_repetitions=4000,analysis_seed=20261013,runs=[])
    summaries={}
    for name in RUN_NAMES:
        run=root/'runs'/name;out=destination/name;out.mkdir()
        m=json.loads((run/'manifest.json').read_text());assert m['status']=='COMPLETE',name
        generations=read_rows(run/'generations.jsonl');assert len(generations)==m['n_generations']==m['completed']
        assert sha(run/'generations.jsonl')==m['output_sha256'],name
        assert sha(run/'code_snapshot.py')==m['code_sha256'],name
        assert sha(run/'generation_code_snapshot.py')==m['generation_code_sha256'],name
        specs=read_rows(run/'generation_specs.jsonl');assert len(specs)==len(generations)
        assert [r['trial_id'] for r in specs]==[r['trial_id'] for r in generations]
        assert all(a['prompt']==b['prompt'] for a,b in zip(specs,generations))
        write_gzip(out/'generations.jsonl.gz',[compact(r) for r in generations])
        write_gzip(out/'generation_specs.jsonl.gz',[compact(r) for r in specs])
        for filename in ['manifest.json','code_snapshot.py','generation_code_snapshot.py','gloss_agent_review.jsonl']:
            if (run/filename).exists():shutil.copyfile(run/filename,out/filename)
        a=summarize(generations)
        write_gzip(out/'decisions.jsonl.gz',[compact(r) for r in a.pop('decisions')])
        decisions=summarize(generations)['decisions']
        metrics=[]
        keys={(r['task'],r['condition'],r.get('split','all')) for r in decisions}
        for task,condition,split in sorted(keys):
            rr=[r for r in decisions if r['task']==task and r['condition']==condition and r.get('split','all')==split]
            metrics.append(dict(task=task,condition=condition,split=split,n_outputs=len(rr),
                correct=sum(r['correct'] for r in rr),family_accuracy=family_metric(rr,'correct')))
        if 'scope-' in name:
            pairs=scope_pairs(decisions);a['scope_pair_groups']=[]
            for split in ['explored','new_family']:
                for discordant in [False,True]:
                    pp=[p for p in pairs if p['split']==split and p['discordant_gold']==discordant]
                    a['scope_pair_groups'].append(dict(split=split,discordant_gold=discordant,n_pairs=len(pp),
                        same_prediction=sum(p['same_prediction'] for p in pp),word_correct=sum(p['word_correct'] for p in pp),
                        predicate_correct=sum(p['predicate_correct'] for p in pp),
                        same_prediction_by_family=family_metric(pp,'same_prediction')))
            a['identical_prompt_answer_mismatches']=sum(not p['same_prediction'] for p in pairs if p['identical_prompt'])
            write_gzip(out/'scope_pairs.jsonl.gz',pairs)
        a.update(run_status='COMPLETE',family_metrics=metrics,
            generation_tasks=dict(Counter(r['task'] for r in generations)),
            hit_token_limit=sum(r['hit_token_limit'] for r in generations))
        (out/'summary.json').write_text(json.dumps(a,ensure_ascii=False,indent=2))
        raw={p.name:dict(sha256=sha(p),bytes=p.stat().st_size) for p in sorted(run.iterdir()) if p.is_file()}
        (out/'raw_provenance.json').write_text(json.dumps(dict(local_raw_run=str(run),original_files=raw),indent=2))
        manifest['runs'].append(dict(name=name,generations=len(generations),tasks=a['generation_tasks'],
            archive_files={p.name:dict(sha256=sha(p),bytes=p.stat().st_size) for p in sorted(out.iterdir()) if p.is_file()}))
        summaries[name]=a
    manifest['total_generations']=sum(r['generations'] for r in manifest['runs'])
    assert len(manifest['runs'])==16 and manifest['total_generations']==21424
    code=destination/'analysis_code';code.mkdir()
    for filename in ['analyze_romance_cycle.py','analyze_doppelganger_diagnostics.py','package_romance_evidence.py',
                     'run_research_generations.py','run_doppelganger_diagnostics.py','build_romance_cycle.py',
                     'build_relation_orthogonal.py','build_lexical_proposition.py','build_scope_followup.py',
                     'build_gloss_explicit_binding.py']:
        shutil.copyfile(root/'scripts'/filename,code/filename)
    manifest['analysis_code_sha256']={p.name:sha(p) for p in sorted(code.iterdir())}
    source_audit=json.loads((root/'data/processed/2026-10-13-romance/manifest.json').read_text())
    (destination/'source_audit.json').write_text(json.dumps(source_audit,indent=2))
    selection=json.loads((root/'data/processed/2026-10-13-romance/gloss_review_selection.json').read_text())
    selection['items']=[{k:v for k,v in r.items() if k not in ['C1','C2']} for r in selection['items']]
    (destination/'gloss_review_selection.json').write_text(json.dumps(selection,ensure_ascii=False,indent=2))
    (destination/'archive_manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2))
    print(f"Archived {len(manifest['runs'])} COMPLETE runs, {manifest['total_generations']} generations")


if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--destination',type=Path,required=True);a=ap.parse_args()
    package(Path(__file__).resolve().parents[1],a.destination)
