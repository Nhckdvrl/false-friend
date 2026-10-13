#!/usr/bin/env python3
"""Freeze published-prompt runs and a separate independent-gloss intervention."""
import csv
import hashlib
import json
from pathlib import Path
import re
import subprocess

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT/'data/raw/false-friends-vs-cognates'
OUT = ROOT/'data/processed/2026-10-13-romance'


def digest(s):
    return hashlib.sha256(s.encode()).hexdigest()


def published_templates():
    lines = (ROOT/'data/raw/reading-2026-10-13/romance.txt').read_text().splitlines()
    e = next(i for i,l in enumerate(lines) if l.startswith('E   Zero-shot prompt'))
    f = next(i for i,l in enumerate(lines) if l.startswith('F   Few-shot prompt'))
    def collect(start,end):
        left = [l[:48].strip() for l in lines[start:end]]
        begin = next(i for i,l in enumerate(left) if l.startswith('Task:'))
        finish = next(i for i,l in enumerate(left[begin:],begin) if l == 'specified.')
        return '\n'.join(left[begin:finish+1])
    zero = collect(e,f)
    few = collect(f,f+55)
    few = re.sub(r'TARGET WORD 1: w1\s+SENTENCE 1: s1', 'TARGET WORD 1: {w1}    SENTENCE 1: {s1}', few)
    few = re.sub(r'TARGET WORD 2: w2\s+SENTENCE 2: s2', 'TARGET WORD 2: {w2}    SENTENCE 2: {s2}', few)
    assert all(x in zero and x in few for x in ('{w1}','{s1}','{w2}','{s2}'))
    assert 'Label: YES' in zero and 'Label: NO' in few and 'Mean Zero' not in zero
    return zero,few


def load_items():
    rows = []
    for p in sorted(SOURCE.glob('*.tsv')):
        subset,pair = p.stem.split('-',1)
        langs = pair.split('-')
        if p.stem == 'auto-es-pt':
            langs.reverse()
        for i,r in enumerate(csv.DictReader(p.open(),delimiter='\t',quoting=csv.QUOTE_NONE)):
            assert None not in r and None not in r.values()
            family = '|'.join(sorted((langs[0]+':'+r['W1'],langs[1]+':'+r['W2'])))
            rows.append(dict(r, item_id=f'{p.stem}:{i}', source_file=p.name, source_row=i+2,
                source_sha='a87b73e387a6ef86d0cef7ffe703150905e75d7a',
                lexeme_family_id=family, subset=subset, language_pair=pair, languages=langs,
                gold_same=int(r['R']), label_provenance='published contextual WiC R'))
    assert len(rows)==704
    return rows


def write(name,rows):
    (OUT/name).write_text(''.join(json.dumps(r,ensure_ascii=False)+'\n' for r in rows))


def main():
    OUT.mkdir(parents=True,exist_ok=False)
    items=load_items(); zero,few=published_templates()
    (OUT/'zero_template.txt').write_text(zero)
    (OUT/'few_template.txt').write_text(few)
    write('items.jsonl',items)
    specs=[]
    for r in items:
        for condition in ['zero_original','zero_swapped']+(['two_shot_original'] if r['language_pair']=='gl-pt' else []):
            a,b = (2,1) if condition=='zero_swapped' else (1,2)
            template = few if condition=='two_shot_original' else zero
            prompt=template.format(w1=r[f'W{a}'],s1=r[f'C{a}'],w2=r[f'W{b}'],s2=r[f'C{b}'])
            specs.append(dict(r, trial_id=r['item_id']+':'+condition, task='romance_wic',
                condition=condition, gold_yes=r['gold_same'], prompt=prompt,
                example_family_overlap=bool({r['W1'],r['W2']} & {'fabricar','brinco'})))
    write('baseline_specs.jsonl',specs)
    human=[r for r in items if r['subset']=='human']
    gloss=[]
    for r in human:
        pool=[x for x in human if x['language_pair']==r['language_pair']]
        idx=pool.index(r)
        distractor=next(pool[(idx+j)%len(pool)] for j in range(1,len(pool))
                        if pool[(idx+j)%len(pool)]['lexeme_family_id']!=r['lexeme_family_id'])
        for side in (1,2):
            other=3-side
            target=f"TARGET\nWord: {r[f'W{side}']}\nSentence: {r[f'C{side}']}"
            question='Explain the meaning of the TARGET word as used in the TARGET sentence. Give only a short English definition, not a translation of the whole sentence. Any other example is a separate usage; the question is only about TARGET.'
            for condition in ('alone','paired_before','paired_after','unrelated_before','unrelated_after'):
                if condition=='alone':
                    body=target; distractor_id=None
                else:
                    d=r if condition.startswith('paired') else distractor
                    extra=f"OTHER EXAMPLE\nWord: {d[f'W{other}']}\nSentence: {d[f'C{other}']}"
                    body=extra+'\n\n'+target if condition.endswith('before') else target+'\n\n'+extra
                    distractor_id=d['item_id']
                gloss.append(dict(r,trial_id=f"{r['item_id']}:side{side}:{condition}",task='independent_gloss',
                    condition=condition,side=side,distractor_id=distractor_id,gloss_gold=None,
                    prompt=question+'\n\n'+body))
    write('gloss_specs.jsonl',gloss)
    manifest=dict(source_sha=subprocess.check_output(['git','-C',str(SOURCE),'rev-parse','HEAD'],text=True).strip(),
        source_files={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in SOURCE.glob('*.tsv')},
        counts=dict(items=len(items),baseline=len(specs),gloss=len(gloss)),
        design='knowledge/notes/ROMANCE_ORTHOGONAL_DESIGN_2026-10-13.md',
        builder_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest())
    (OUT/'manifest.json').write_text(json.dumps(manifest,indent=2))
    print(json.dumps(manifest['counts']))


if __name__=='__main__':
    main()
