#!/usr/bin/env python3
"""Authored meaning/reference factorial; no source labels are inherited."""
import hashlib
import json
from pathlib import Path

JOBS = [
    ('dentist','牙医'),('baker','面包师'),('violinist','小提琴手'),('plumber','水管工'),
    ('architect','建筑师'),('carpenter','木匠'),('nurse','护士'),('painter','画家'),
    ('farmer','农民'),('tailor','裁缝'),('pilot','飞行员'),('librarian','图书管理员'),
    ('electrician','电工'),('photographer','摄影师'),('accountant','会计师'),('translator','翻译员'),
    ('firefighter','消防员'),('singer','歌手'),('dancer','舞蹈演员'),('gardener','园丁'),
    ('programmer','程序员'),('lawyer','律师'),('astronomer','天文学家'),('veterinarian','兽医'),
]


def build():
    trials=[]
    for i,(word,zh) in enumerate(JOBS):
        different=JOBS[(i+12)%len(JOBS)][0]
        for language in ('en-en','zh-en'):
            w1=word if language=='en-en' else zh
            s1=f'Amira Chen is a {word}.' if language=='en-en' else f'Amira Chen 是一名{zh}。'
            for same_meaning in (0,1):
                w2=word if same_meaning else different
                for same_person in (0,1):
                    name='Amira Chen' if same_person else 'Nora Silva'
                    s2=f'{name} is a {w2}.'
                    base=("In these descriptions, repeated full names identify the same person, and different full names identify different people. A person may have more than one occupation.\n"
                          f'Description 1: {s1}\nTarget word 1: {w1}\nDescription 2: {s2}\nTarget word 2: {w2}\n')
                    for relation in ('meaning','person'):
                        for polarity in ('same','different'):
                            if relation=='meaning':
                                question=f'Do the two target words have {"the same occupational meaning" if polarity=="same" else "different occupational meanings"}, regardless of who has the occupation?'
                                same=same_meaning
                            else:
                                question=f'Do the people described by the two target words have {"the same personal identity" if polarity=="same" else "different personal identities"}, regardless of their occupations?'
                                same=same_person
                            ident=f'{word}:{language}:meaning{same_meaning}:person{same_person}:{relation}:{polarity}'
                            trials.append(dict(trial_id=ident,item_id=ident,task='orthogonal_relation',
                                lexeme_family_id=word,contrast_word=different,language_pair=language,
                                same_meaning=same_meaning,same_person=same_person,relation=relation,polarity=polarity,
                                condition=f'{relation}:{polarity}',gold_yes=same if polarity=='same' else 1-same,
                                label_provenance='agent-authored and locally reviewed; no independent human review',
                                prompt=base+'\n'+question+'\nBegin with YES or NO, then give one short sentence explaining your answer.'))
    assert len(trials)==768 and len({r['trial_id'] for r in trials})==768
    return trials


def main():
    root=Path(__file__).resolve().parents[1]
    out=root/'experiments/stimuli/relation_orthogonal_2026-10-13.jsonl'
    assert not out.exists()
    rows=build()
    out.write_text(''.join(json.dumps(r,ensure_ascii=False)+'\n' for r in rows))
    combined=root/'data/processed/2026-10-13-romance/exploration_specs.jsonl'
    combined.write_text(out.read_text()+(combined.parent/'gloss_specs.jsonl').read_text())
    print(dict(authored=len(rows),combined=len(combined.read_text().splitlines()),sha256=hashlib.sha256(out.read_bytes()).hexdigest()))


if __name__=='__main__':
    main()
