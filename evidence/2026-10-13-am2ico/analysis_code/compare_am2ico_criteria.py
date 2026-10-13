#!/usr/bin/env python3
"""Paired, family-clustered criterion contrasts, including negative examples."""
import argparse
from collections import defaultdict
import json
from pathlib import Path
try:
    from scripts.analyze_doppelganger_diagnostics import bootstrap
except ModuleNotFoundError:
    from analyze_doppelganger_diagnostics import bootstrap


def rows(path):return [json.loads(x) for x in path.read_text().splitlines()]


def compare(parent,followup):
    decisions=rows(parent/'decisions.jsonl')+rows(followup/'decisions.jsonl')
    lookup={(r['item_id'],r['representation']):r for r in decisions}
    out=[]
    for language in ['all','de','zh','ja']:
        for label in ['all','T','F']:
            rr=[r for r in decisions if r['representation']=='full' and (language=='all' or r['language']==language) and (label=='all' or r['source_label']==label)]
            for criterion in ['target_only','sense_basic','sense_explicit']:
                vals=defaultdict(list);rescues=losses=0
                for r in rr:
                    other=lookup[(r['item_id'],criterion)]
                    delta=int(other['source_label_agreement'])-int(r['source_label_agreement'])
                    vals[r['lexeme_family_id']].append(delta);rescues+=delta>0;losses+=delta<0
                out.append({'language':language,'source_label':label,'contrast':criterion+' minus full',
                            'n_items':len(rr),'paired_delta':bootstrap(vals),'rescued_source_agreement':rescues,'lost_source_agreement':losses})
    (followup/'criterion_contrasts.json').write_text(json.dumps(out,ensure_ascii=False,indent=2))
    for r in out:
        if r['language']=='all':print(r)


if __name__=='__main__':
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('parent',type=Path);ap.add_argument('followup',type=Path)
    args=ap.parse_args();compare(args.parent,args.followup)
