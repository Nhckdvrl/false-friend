#!/usr/bin/env python3
"""Paired target changes and published-label agreement; no inferred human gold."""
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


def rows(path):return [json.loads(x) for x in path.read_text().splitlines()]


def analyze(run):
    raw=rows(run/'trials.jsonl');grouped=defaultdict(list)
    for r in raw:grouped[(r['item_id'],r['representation'])].append(r)
    decisions=[]
    for _,rr in grouped.items():
        assert len(rr)==2 and {r['rotation'] for r in rr}=={0,1}
        r=rr[0];scores=[0.,0.];choices=[]
        for row in rr:
            choices.append(row['content_order'][max(range(2),key=row['label_logps'].__getitem__)])
            for j,c in enumerate(row['content_order']):scores[c]+=row['label_logps'][j]/2
        pred=max(range(2),key=scores.__getitem__)
        decisions.append({k:r[k] for k in ['item_id','pair_id','lexeme_family_id','language','source_line','source_label','targets','changed_side','representation','original_label_index']} |
                         {'prediction':pred,'source_label_agreement':pred==r['original_label_index'],
                          'all_orders_agree_source':all(p==r['original_label_index'] for p in choices),
                          'stable':len(set(choices))==1,'rotation_choices':choices,'content_logps':scores,
                          'exact_score_tie':scores[0]==scores[1],
                          'interpretation':'Original-label agreement; target_only not a semantic gold task.'})
    ps=defaultdict(dict)
    for r in decisions:ps[(r['pair_id'],r['representation'])][r['source_label']]=r
    pairs=[]
    for (pairid,rep),rr in ps.items():
        p,n=rr['T'],rr['F']
        pairs.append({'pair_id':pairid,'lexeme_family_id':p['lexeme_family_id'],'language':p['language'],'representation':rep,
                      'changed_side':p['changed_side'],'positive_targets':p['targets'],'negative_targets':n['targets'],
                      'predictions':[p['prediction'],n['prediction']],
                      'both_source_labels_matched':p['source_label_agreement'] and n['source_label_agreement'],
                      'both_labels_all_orders_matched':p['all_orders_agree_source'] and n['all_orders_agree_source'],
                      'prediction_changes_with_target':p['prediction']!=n['prediction']})
    summaries=[]
    representations=list(dict.fromkeys(r['representation'] for r in decisions))
    for language in ['de','zh','ja']:
        for representation in representations:
            rr=[r for r in decisions if r['language']==language and r['representation']==representation]
            pp=[r for r in pairs if r['language']==language and r['representation']==representation]
            metrics={}
            for metric in ['source_label_agreement','all_orders_agree_source','stable']:
                vals=defaultdict(list)
                for r in rr:vals[r['lexeme_family_id']].append(float(r[metric]))
                metrics[metric]=bootstrap(vals)
            for metric in ['both_source_labels_matched','both_labels_all_orders_matched','prediction_changes_with_target']:
                vals=defaultdict(list)
                for r in pp:vals[r['lexeme_family_id']].append(float(r[metric]))
                metrics[metric]=bootstrap(vals)
            by_label={label:sum(r['source_label_agreement'] for r in rr if r['source_label']==label)/sum(r['source_label']==label for r in rr) for label in ['T','F']}
            summaries.append({'language':language,'representation':representation,'n_pairs':len(pp),'metrics':metrics,'agreement_by_source_label':by_label})
    generation_audit=[]
    if (run/'generations.jsonl').exists():
        for i,r in enumerate(rows(run/'generations.jsonl')):
            if r['generation_task']!='joint_relation':continue
            match=re.match(r'^\s*[\*"\x27]*([AB])(?:\b|[).:])',r['generated']);letter=match.group(1) if match else None
            choice=r['content_order']['AB'.index(letter)] if letter else None
            generation_audit.append({'row_index':i,'item_id':r['item_id'],'pair_id':r['pair_id'],'letter':letter,
                                     'choice':choice,'source_label_agreement':choice==r['original_label_index'] if choice is not None else None,
                                     'hit_token_limit':r['hit_token_limit'],'semantic_review':'UNREVIEWED'})
    masses=[sum(math.exp(p) for p in r['label_logps']) for r in raw]
    summary={'status':json.loads((run/'manifest.json').read_text())['status'],'n_trials':len(raw),
             'n_pairs':len(pairs)//len(representations),'n_lexeme_families':len({r['lexeme_family_id'] for r in decisions}),
             'groups':summaries,'format_audit':{'min_label_mass':min(masses),'mean_label_mass':sum(masses)/len(masses),
                                             'off_label_argmax':sum(r['unrestricted_argmax_token'] not in r['label_token_ids'] for r in raw)},
             'interpretation':'Adaptation on original labelled source pairs, not faithful encoder replication. Agreement is not independently validated semantic accuracy; source span and granularity require review.'}
    for name,data in [('decisions.jsonl',decisions),('paired_predictions.jsonl',pairs),('generation_checks.jsonl',generation_audit)]:
        (run/name).write_text(''.join(json.dumps(r,ensure_ascii=False)+'\n' for r in data))
    (run/'summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2))
    print(run,summary['status'],summary['format_audit'])
    for r in summaries:
        m=r['metrics'];print(r['language'],r['representation'],'agreement',round(m['source_label_agreement']['mean'],3),
              'both',round(m['both_source_labels_matched']['mean'],3),'all-orders',round(m['both_labels_all_orders_matched']['mean'],3),r['agreement_by_source_label'])


if __name__=='__main__':
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('runs',nargs='+',type=Path)
    for run in ap.parse_args().runs:analyze(run)
