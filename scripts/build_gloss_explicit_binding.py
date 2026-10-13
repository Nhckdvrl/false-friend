#!/usr/bin/env python3
"""Post-run reconstruction helper, checked against the original frozen 180 specs."""
import argparse
import json
from pathlib import Path


def build(specs,selection):
    ids={r['item_id'] for r in selection['items']};out=[]
    for r in specs:
        if r['item_id'] not in ids:continue
        target=r[f'W{r["side"]}']
        body=r['prompt'].split('\n\n',1)[1].replace('TARGET\n','DESIGNATED SENTENCE\n')
        prompt=(f'Give a short English definition of the word "{target}" in the DESIGNATED SENTENCE below. An OTHER EXAMPLE, if supplied, is a separate usage.\n\n'
                +body+f'\n\nQuestion: What does "{target}" mean in the DESIGNATED SENTENCE? Define that word only.')
        out.append(dict(r,trial_id=r['trial_id']+':explicit_binding',prompt=prompt,
            protocol='gloss-explicit-binding-followup',parent_trial_id=r['trial_id']))
    assert len(out)==180
    return out


if __name__=='__main__':
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--input',type=Path,default=Path('data/processed/2026-10-13-romance/gloss_specs.jsonl'))
    ap.add_argument('--selection',type=Path,default=Path('evidence/2026-10-13-romance-scope/gloss_review_selection.json'))
    ap.add_argument('--output',type=Path,default=Path('data/processed/2026-10-13-romance/gloss_explicit_binding_specs.jsonl'))
    a=ap.parse_args();specs=[json.loads(x) for x in a.input.read_text().splitlines()]
    rows=build(specs,json.loads(a.selection.read_text()))
    text=''.join(json.dumps(r,ensure_ascii=False)+'\n' for r in rows)
    if a.output.exists():
        assert a.output.read_text()==text, 'Existing frozen specs differ; do not overwrite.'
        print('Reconstructed specs exactly match the frozen file.')
    else:
        a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(text)
        print(f'Wrote {len(rows)} frozen specs.')
