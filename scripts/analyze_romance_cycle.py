#!/usr/bin/env python3
"""Explicit generated answers; never interpret gloss string edits as sense changes."""
import argparse
from collections import defaultdict
import json
from pathlib import Path
import re


def parse_answer(text, task):
    prefix=r'^\s*[*"\x27]*(?:Label\s*:\s*[*"\x27\s]*)' if task=='romance_wic' else r'^\s*[*"\x27]*(?:Answer\s*:\s*[*"\x27\s]*)?'
    m=re.match(prefix+r'(YES|NO)\b',text,re.I)
    return int(m.group(1).lower()=='yes') if m else None


def explicit_label(text):
    """Sensitivity readout: unique explicit Label line, allowing a preamble."""
    found=re.findall(r'^\s*[*"\x27]*Label[*"\x27]*\s*:\s*[*"\x27]*(YES|NO)\b',text,re.I|re.M)
    values={x.lower() for x in found}
    return int(next(iter(values))=='yes') if len(values)==1 else None


def summarize(rows):
    groups=defaultdict(list)
    parsed=[]
    for r in rows:
        if r['task']=='independent_gloss':
            continue
        p=parse_answer(r['generated'],r['task'])
        d={k:v for k,v in r.items() if k not in ('prompt','rendered_prompt','generated_token_ids')}
        d.update(prediction=p,correct=p==r['gold_yes'],parsed=p is not None)
        if r['task']=='romance_wic':
            alt=explicit_label(r['generated'])
            d.update(explicit_label=alt,explicit_label_correct=alt==r['gold_yes'])
        parsed.append(d)
        key=(r['task'],r['condition'],r['language_pair'],r.get('subset','authored'))
        groups[key].append(d)
    stats=[]
    for key,rr in sorted(groups.items()):
        stats.append(dict(task=key[0],condition=key[1],language_pair=key[2],subset=key[3],n=len(rr),
            correct=sum(r['correct'] for r in rr),parsed=sum(r['parsed'] for r in rr),
            yes=sum(r['prediction']==1 for r in rr),token_limit=sum(r['hit_token_limit'] for r in rr),
            explicit_label_correct=sum(r.get('explicit_label_correct',False) for r in rr) if key[0]=='romance_wic' else None))
    index={(r['item_id'],r['condition']):r for r in parsed if r['task']=='romance_wic'}
    symmetry=[]
    for (item,condition),r in index.items():
        other=index.get((item,'zero_swapped'))
        if condition!='zero_original' or other is None:
            continue
        symmetry.append(dict(item_id=item,lexeme_family_id=r['lexeme_family_id'],language_pair=r['language_pair'],
            subset=r['subset'],gold_same=r['gold_same'],original=r['prediction'],swapped=other['prediction'],
            both_parsed=r['parsed'] and other['parsed'],consistent=r['parsed'] and other['parsed'] and r['prediction']==other['prediction'],
            both_correct=r['correct'] and other['correct'],delta_correct=int(other['correct'])-int(r['correct'])))
    cells=defaultdict(list)
    for r in parsed:
        if r['task']=='orthogonal_relation':
            cells[(r['language_pair'],r['relation'],r['polarity'],r['same_meaning'],r['same_person'])].append(r)
    factorial=[dict(language_pair=k[0],relation=k[1],polarity=k[2],same_meaning=k[3],same_person=k[4],
        n=len(rr),correct=sum(r['correct'] for r in rr),unparsed=sum(not r['parsed'] for r in rr)) for k,rr in sorted(cells.items())]
    return dict(groups=stats,symmetry=symmetry,factorial=factorial,decisions=parsed)


def main():
    ap=argparse.ArgumentParser();ap.add_argument('runs',nargs='+',type=Path);a=ap.parse_args()
    for run in a.runs:
        path=run/'generations.jsonl'
        if not path.exists():
            continue
        rows=[json.loads(l) for l in path.read_text().splitlines()]
        result=summarize(rows);result['run_status']=json.loads((run/'manifest.json').read_text())['status']
        (run/'analysis.json').write_text(json.dumps(result,ensure_ascii=False,indent=2))
        aggregate=defaultdict(lambda:[0,0,0])
        for r in result['decisions']:
            key=r['task']+':'+r['condition'];aggregate[key][0]+=1;aggregate[key][1]+=r['correct'];aggregate[key][2]+=not r['parsed']
        print(run.name,result['run_status'],dict(aggregate),'symmetry',len(result['symmetry']),sum(x['consistent'] for x in result['symmetry']))


if __name__=='__main__':
    main()
