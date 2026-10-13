#!/usr/bin/env python3
"""Compare complete initial answers with restricted first-token label decisions."""
import argparse
from collections import defaultdict
import json
from pathlib import Path
import re
try:
    from scripts.analyze_doppelganger_diagnostics import bootstrap
except ModuleNotFoundError:
    from analyze_doppelganger_diagnostics import bootstrap


def parse_initial_answer(text, order):
    lines = [x.strip() for x in text.splitlines() if x.strip()]
    if not lines:
        return {'choice': None, 'parse_status': 'empty', 'initial_line': ''}
    line = lines[0]
    # A is also an English article. Require punctuation or an explicit answer cue.
    letters = re.findall(r'\b([AB])\s*[).:]|(?:answer|option|Antwort|Option|Wahl)\s+(?:is\s+|ist\s+)?([AB])\b', line, re.I)
    letters = {a or b for a,b in letters}
    letters = {x.upper() for x in letters}
    if re.fullmatch(r'[\s*"\x27]*[AB][\s*"\x27]*', line):
        letters.add(re.sub(r'[\s*"\x27]', '', line))
    codes = set(re.findall(r'\b(Cedar|Maple)\b', line, re.I))
    choices = {order['AB'.index(x)] for x in letters}
    choices.update(0 if c.lower() == 'cedar' else 1 for c in codes)
    status = 'explicit_unique' if len(choices) == 1 else ('conflicting' if choices else 'no_explicit_initial_answer')
    return {'choice': next(iter(choices)) if len(choices) == 1 else None,
            'parse_status': status, 'initial_line': line, 'letters': sorted(letters), 'codes': sorted(codes)}


def key(r):
    return tuple(r[k] for k in ('item_id','representation','mapping','rotation','explanation_language'))


def analyze(run):
    manifest = json.loads((run/'manifest.json').read_text())
    parent = Path(manifest['parent_run'])
    trials = {key(r):r for r in map(json.loads,(parent/'trials.jsonl').read_text().splitlines()) if r['task']=='rule'}
    reviews = []
    for i,r in enumerate(map(json.loads,(run/'generations.jsonl').read_text().splitlines())):
        t = trials[key(r)]
        assert r['rendered_prompt_sha256'] == t['rendered_prompt_sha256']
        parse = parse_initial_answer(r['generated'],r['content_order'])
        restricted = r['content_order'][max(range(2),key=t['label_logps'].__getitem__)]
        reviews.append({k:r[k] for k in ('item_id','lexeme_family_id','group','representation','mapping','rotation','explanation_language','correct_index')} |
                       {'row_index':i, **parse, 'natural_answer_correct':parse['choice']==r['correct_index'] if parse['choice'] is not None else None,
                        'restricted_choice':restricted, 'restricted_correct':restricted==r['correct_index'],
                        'first_token_allowed':bool(r['generated_token_ids']) and r['generated_token_ids'][0] in t['label_token_ids'],
                        'first_token_matches_scoring_argmax':bool(r['generated_token_ids']) and r['generated_token_ids'][0]==t['unrestricted_argmax_token'],
                        'hit_token_limit':r['hit_token_limit'], 'explanation_review':'UNREVIEWED'})
    groups = defaultdict(list)
    for r in reviews:
        groups[(r['group'],r['representation'],r['explanation_language'])].append(r)
    summaries=[]
    for k,rr in groups.items():
        metrics = {}
        # Missing/ambiguous natural answers are failures for the unconditional
        # explicit-answer rate, not silently excluded from the denominator.
        for metric in ('natural_answer_correct','restricted_correct','first_token_allowed'):
            vals=defaultdict(list)
            for r in rr: vals[r['lexeme_family_id']].append(float(bool(r[metric])))
            metrics[metric]=bootstrap(vals)
        rescued=sum(r['natural_answer_correct'] is True and not r['restricted_correct'] for r in rr)
        lost=sum(r['natural_answer_correct'] is False and r['restricted_correct'] for r in rr)
        summaries.append({'group':k[0],'representation':k[1],'explanation_language':k[2], 'n':len(rr),'metrics':metrics,
                          'unparsed':sum(r['choice'] is None for r in rr),'rescued':rescued,'lost':lost,
                          'token_limit':sum(r['hit_token_limit'] for r in rr)})
    (run/'answer_audit.jsonl').write_text(''.join(json.dumps(r,ensure_ascii=False)+'\n' for r in reviews))
    summary={'n_generations':len(reviews),'groups':summaries,
             'unparsed':sum(r['choice'] is None for r in reviews),
             'first_token_argmax_disagreements':sum(not r['first_token_matches_scoring_argmax'] for r in reviews),
             'interpretation':'Initial explicit answer parser, not semantic explanation grading; all output retained. Off-label paths and batch-dependent near-ties can change decisions.'}
    (run/'summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2))
    print(run, 'unparsed',summary['unparsed'],'argmax disagreements',summary['first_token_argmax_disagreements'])
    for r in summaries:
        if r['representation']=='original':
            print(r['group'],r['explanation_language'],'natural',round(r['metrics']['natural_answer_correct']['mean'],3),
                  'restricted',round(r['metrics']['restricted_correct']['mean'],3),'rescued',r['rescued'],'lost',r['lost'])


if __name__=='__main__':
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('runs',type=Path,nargs='+')
    for run in ap.parse_args().runs: analyze(run)
