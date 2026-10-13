#!/usr/bin/env python3
"""Same/different question polarity and fixed-gloss context addback diagnostics."""
import argparse
from collections import defaultdict
import json
import math
from pathlib import Path
import re
try:
    from scripts.analyze_doppelganger_diagnostics import bootstrap
except ModuleNotFoundError:
    from analyze_doppelganger_diagnostics import bootstrap


def rows(p):return [json.loads(x) for x in p.read_text().splitlines()]


def parse_yes_no(text):
    # Only an explicit opening answer; never infer the decision from an explanation.
    m=re.match(r'^\s*[\*"\x27]*(?:Answer\s*:\s*[\*"\x27\s]*)?(Yes|No)\b',text,re.I)
    return m.group(1).lower() if m else None


def analyze(run):
    raw=rows(run/'trials.jsonl');gg=defaultdict(list)
    for r in raw:gg[(r['item_id'],r['representation'])].append(r)
    decisions=[]
    for _,rr in gg.items():
        assert len(rr)==2 and {r['polarity'] for r in rr}=={'same','different'}
        r=rr[0];scores=[0.,0.];choices={}
        for t in rr:
            choices[t['polarity']]=t['content_order'][max(range(2),key=t['label_logps'].__getitem__)]
            for j,c in enumerate(t['content_order']):scores[c]+=t['label_logps'][j]/2
        pred=max(range(2),key=scores.__getitem__)
        decisions.append({k:r[k] for k in ['item_id','pair_id','lexeme_family_id','language','targets','source_label','representation','original_label_index','gloss_hashes']} |
            {'prediction':pred,'source_label_agreement':pred==r['original_label_index'],
             'both_polarities_agree_source':all(v==r['original_label_index'] for v in choices.values()),
             'polarity_consistent':len(set(choices.values()))==1,'polarity_predictions':choices,'content_logps':scores})
    summaries=[]
    for representation in ['raw_only','gloss_only','raw_plus_gloss']:
        for label in ['all','T','F']:
            rr=[r for r in decisions if r['representation']==representation and (label=='all' or r['source_label']==label)]
            metrics={}
            for metric in ['source_label_agreement','both_polarities_agree_source','polarity_consistent']:
                vals=defaultdict(list)
                for r in rr:vals[r['lexeme_family_id']].append(float(r[metric]))
                metrics[metric]=bootstrap(vals)
            summaries.append({'representation':representation,'source_label':label,'n_items':len(rr),'metrics':metrics})
    lookup={(r['item_id'],r['representation']):r for r in decisions};contrasts=[];flips=[]
    for label in ['all','T','F']:
        vals=defaultdict(list)
        for r in decisions:
            if r['representation']!='gloss_only' or (label!='all' and r['source_label']!=label):continue
            other=lookup[(r['item_id'],'raw_plus_gloss')]
            assert r['gloss_hashes']==other['gloss_hashes']
            vals[r['lexeme_family_id']].append(int(other['source_label_agreement'])-int(r['source_label_agreement']))
            if label=='all' and r['prediction']!=other['prediction']:flips.append({'gloss_only':r,'raw_plus_gloss':other})
        contrasts.append({'source_label':label,'raw_plus_gloss_minus_gloss_only':bootstrap(vals)})
    generation_audit=[]
    if (run/'generations.jsonl').exists():
        for i,r in enumerate(rows(run/'generations.jsonl')):
            answer=parse_yes_no(r['generated'])
            pred=r['content_order'][0 if answer=='yes' else 1] if answer else None
            generation_audit.append({k:r[k] for k in ['item_id','pair_id','lexeme_family_id','representation','polarity','source_label']} |
                {'row_index':i,'answer':answer,'prediction':pred,'source_label_agreement':pred==r['original_label_index'] if pred is not None else None,
                 'hit_token_limit':r['hit_token_limit'],'semantic_review':'UNREVIEWED'})
    masses=[sum(math.exp(p) for p in r['label_logps']) for r in raw]
    natural_summary=[];natural_contrasts=[]
    if generation_audit:
        glookup={(r['item_id'],r['representation'],r['polarity']):r for r in generation_audit}
        for representation in ['raw_only','gloss_only','raw_plus_gloss']:
            rr=[r for r in generation_audit if r['representation']==representation]
            vals=defaultdict(list)
            for r in rr:vals[r['lexeme_family_id']].append(float(bool(r['source_label_agreement'])))
            natural_summary.append({'representation':representation,'n_outputs':len(rr),'unparsed':sum(r['answer'] is None for r in rr),
                                    'token_limit':sum(r['hit_token_limit'] for r in rr),'explicit_answer_agreement':bootstrap(vals)})
        for label in ['all','T','F']:
            vals=defaultdict(list)
            for r in generation_audit:
                if r['representation']!='gloss_only' or (label!='all' and r['source_label']!=label):continue
                other=glookup[(r['item_id'],'raw_plus_gloss',r['polarity'])]
                vals[r['lexeme_family_id']].append(float(bool(other['source_label_agreement']))-float(bool(r['source_label_agreement'])))
            natural_contrasts.append({'source_label':label,'raw_plus_gloss_minus_gloss_only':bootstrap(vals)})
    summary={'status':json.loads((run/'manifest.json').read_text())['status'],'groups':summaries,'contrasts':contrasts,
             'natural_output_groups':natural_summary,'natural_output_contrasts':natural_contrasts,
             'n_addback_prediction_flips':len(flips),'format_audit':{'min_label_mass':min(masses),'mean_label_mass':sum(masses)/len(masses),
             'off_label_argmax':sum(r['unrestricted_argmax_token'] not in r['label_token_ids'] for r in raw)},
             'interpretation':'Two question polarities, not option permutations. Aggregated content score is a diagnostic, not a latent sense posterior. Own glosses fixed across paired addback; original labels not independently validated.'}
    for name,rr in [('decisions.jsonl',decisions),('addback_flips.jsonl',flips),('generation_checks.jsonl',generation_audit)]:
        (run/name).write_text(''.join(json.dumps(r,ensure_ascii=False)+'\n' for r in rr))
    (run/'summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2))
    print(run,summary['status'],summary['format_audit'])
    for r in summaries:
        print(r['representation'],r['source_label'],'agreement',round(r['metrics']['source_label_agreement']['mean'],3),
              'both-polarities',round(r['metrics']['both_polarities_agree_source']['mean'],3))
    print('contrasts',contrasts)
    if natural_summary:print('natural_outputs',natural_summary,'natural_contrasts',natural_contrasts)


if __name__=='__main__':
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('runs',type=Path,nargs='+')
    for run in ap.parse_args().runs:analyze(run)
