#!/usr/bin/env python3
"""Natural-answer contrasts for strictly matched context and target additions."""
import argparse
from collections import defaultdict
import json
from pathlib import Path
try:
    from scripts.analyze_gloss_addback import parse_yes_no, rows
    from scripts.analyze_doppelganger_diagnostics import bootstrap
except ModuleNotFoundError:
    from analyze_gloss_addback import parse_yes_no, rows
    from analyze_doppelganger_diagnostics import bootstrap


def analyze(run):
    manifest=json.loads((run/'manifest.json').read_text())
    parent=Path(manifest['parent_run'])
    if not parent.exists():parent=run.parent/parent.name
    audit=[]
    for path in [parent,run]:
        for i,r in enumerate(rows(path/'generations.jsonl')):
            ans=parse_yes_no(r['generated'])
            pred=r['content_order'][0 if ans=='yes' else 1] if ans else None
            audit.append({k:r[k] for k in ['item_id','pair_id','lexeme_family_id','representation','polarity','source_label']} |
                         {'run':path.name,'row_index':i,'answer':ans,'prediction':pred,
                          'source_label_agreement':pred==r['original_label_index'] if pred is not None else None,
                          'hit_token_limit':r['hit_token_limit']})
    groups=[]
    for rep in sorted({r['representation'] for r in audit}):
        for label in ['all','T','F']:
            rr=[r for r in audit if r['representation']==rep and (label=='all' or r['source_label']==label)]
            vals=defaultdict(list)
            for r in rr:vals[r['lexeme_family_id']].append(float(bool(r['source_label_agreement'])))
            groups.append({'representation':rep,'source_label':label,'n_outputs':len(rr),
                           'unparsed':sum(r['answer'] is None for r in rr),'token_limit':sum(r['hit_token_limit'] for r in rr),
                           'explicit_answer_agreement':bootstrap(vals)})
    comparisons=[('raw_targets_gloss','gloss_only'),('raw_targets_gloss','raw_plus_gloss'),
                 ('raw_targets','raw_only'),('raw_targets_gloss','raw_targets')]
    lookup={(r['item_id'],r['representation'],r['polarity']):r for r in audit}
    polarity_groups=[]
    for rep in sorted({r['representation'] for r in audit}):
        rr=[r for r in audit if r['representation']==rep]
        vals=defaultdict(list);both=defaultdict(list)
        for r in rr:
            if r['polarity']!='same':continue
            other=lookup[(r['item_id'],rep,'different')]
            vals[r['lexeme_family_id']].append(float(r['prediction'] is not None and r['prediction']==other['prediction']))
            both[r['lexeme_family_id']].append(float(bool(r['source_label_agreement']) and bool(other['source_label_agreement'])))
        cells=[]
        for pol in ['same','different']:
            for label in ['T','F']:
                ss=[r for r in rr if r['polarity']==pol and r['source_label']==label]
                cells.append({'polarity':pol,'source_label':label,'n_outputs':len(ss),
                              'source_agreement_count':sum(bool(r['source_label_agreement']) for r in ss),
                              'no_count':sum(r['answer']=='no' for r in ss)})
        polarity_groups.append({'representation':rep,'cells':cells,'polarity_consistency':bootstrap(vals),
                                'both_polarities_agree_source':bootstrap(both)})
    contrasts=[];flips=[]
    for added,base in comparisons:
        for label in ['all','T','F']:
            vals=defaultdict(list)
            for r in audit:
                if r['representation']!=base or (label!='all' and r['source_label']!=label):continue
                other=lookup[(r['item_id'],added,r['polarity'])]
                vals[r['lexeme_family_id']].append(float(bool(other['source_label_agreement']))-float(bool(r['source_label_agreement'])))
                if label=='all' and r['prediction']!=other['prediction']:flips.append({'comparison':added+' minus '+base,'base':r,'added':other})
            contrasts.append({'comparison':added+' minus '+base,'source_label':label,'paired_difference':bootstrap(vals)})
    summary={'status':manifest['status'],'parent_status':json.loads((parent/'manifest.json').read_text())['status'],
             'groups':groups,'contrasts':contrasts,'polarity_groups':polarity_groups,
             'interpretation':'Exploratory matched contrasts on the same frozen 24-family generation subset. Initial explicit answer agreement with source labels, not human-validated semantic accuracy or explanation correctness. Both question polarities repeated within families; unparsed retained as failures.'}
    for filename,rr in [('combined_answer_audit.jsonl',audit),('natural_flips.jsonl',flips)]:
        (run/filename).write_text(''.join(json.dumps(r,ensure_ascii=False)+'\n' for r in rr))
    (run/'summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2))
    print(run,summary['status'])
    for r in groups:
        if r['source_label']=='all':print(r)
    for r in contrasts:
        if r['source_label']=='all':print(r)


if __name__=='__main__':
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('runs',type=Path,nargs='+')
    for run in ap.parse_args().runs:analyze(run)
