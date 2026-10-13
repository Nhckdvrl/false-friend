#!/usr/bin/env python3
"""Hold sentences and question fixed; move only the highlighted target boundary."""
from pathlib import Path
import json
from scripts.build_lexical_proposition import DOMAINS

NEW=[('request','approved','unapproved'),('seat','reserved','unreserved'),
     ('session','authenticated','unauthenticated'),('option','selected','unselected'),
     ('address','reachable','unreachable'),('vehicle','registered','unregistered'),
     ('document','public','private'),('file','encrypted','unencrypted'),
     ('set','finite','infinite'),('object','divisible','indivisible'),
     ('clock','synchronized','unsynchronized'),('component','attached','detached')]


def build():
    domains=[(n,w0,w1,'explored') for n,_,w0,w1,_,_ in DOMAINS]+[(n,w0,w1,'new_family') for n,w0,w1 in NEW]
    out=[]
    for noun,w0,w1,split in domains:
        for first in (0,1):
            for same in (0,1):
                second=first if same else 1-first;a=(w0,w1)[first];b=(w0,w1)[second]
                common=dict(task='scope_followup',lexeme_family_id=w0,language_pair='en-en',split=split,
                            first=first,second=second,same_word=same,label_provenance='agent-authored binary-domain semantics')
                isolated=f'Expression 1: {a}\nExpression 2: {b}\nDo these expressions have the same lexical meaning? Begin with YES or NO, then explain in one short sentence.'
                out.append(dict(common,condition='isolated',gold_yes=same,trial_id=f'{w0}:first{first}:same{same}:isolated',prompt=isolated))
                for n1 in (0,1):
                    for n2 in (0,1):
                        prop=int((first^n1)==(second^n2))
                        for scope in ('word','predicate'):
                            def sentence(w,n):
                                phrase=('not ' if n else '')+w
                                marked=(('not ' if n else '')+f'<target>{w}</target>' if scope=='word'
                                        else f'<target>{phrase}</target>')
                                return f'The {noun} is {marked}.'
                            prompt=(f'Compare two alternative descriptions of the same {noun} at the same instant. Neither description is assumed to be true. For this task its status has exactly two mutually exclusive possibilities: {w0} and {w1}.\n'
                                    f'Sentence 1: {sentence(a,n1)}\nSentence 2: {sentence(b,n2)}\n'
                                    'Do the two expressions enclosed by <target> and </target> have the same meaning in these sentences? Begin with YES or NO, then explain in one short sentence.')
                            out.append(dict(common,condition=scope,negation_1=n1,negation_2=n2,same_proposition=prop,
                                gold_yes=same if scope=='word' else prop,
                                trial_id=f'{w0}:first{first}:same{same}:neg{n1}{n2}:{scope}',prompt=prompt))
    assert len(out)==864 and len({r['trial_id'] for r in out})==864
    return [{**r,'item_id':r['trial_id']} for r in out]


if __name__=='__main__':
    p=Path('experiments/stimuli/scope_followup_2026-10-13.jsonl')
    assert not p.exists()
    p.write_text(''.join(json.dumps(r,ensure_ascii=False)+'\n' for r in build()))
    print(len(build()))
