#!/usr/bin/env python3
"""Frozen Boolean lexical/propositional contrast with explicitly binary domains."""
from pathlib import Path
import json

DOMAINS=[
 ('account','账户','active','inactive','活跃','不活跃'),
 ('feature','功能','enabled','disabled','启用','禁用'),
 ('door','门','locked','unlocked','上锁','未上锁'),
 ('cable','电缆','connected','disconnected','连接','断开'),
 ('student','学生','present','absent','在场','缺席'),
 ('room','房间','occupied','vacant','有人占用','空置'),
 ('permit','许可证','valid','invalid','有效','无效'),
 ('symbol','符号','visible','invisible','可见','不可见'),
 ('action','行为','legal','illegal','合法','违法'),
 ('person','人','married','unmarried','已婚','未婚'),
 ('server','服务器','online','offline','在线','离线'),
 ('valve','阀门','open','closed','打开','关闭'),
]


def build():
    rows=[]
    for noun,zh_noun,w0,w1,z0,z1 in DOMAINS:
        for lang in ('en-en','zh-en'):
            for first in (0,1):
                for same_word in (0,1):
                    second=first if same_word else 1-first
                    t1=(w0,w1)[first] if lang=='en-en' else (z0,z1)[first]
                    t2=(w0,w1)[second]
                    for n1 in (0,1):
                        for n2 in (0,1):
                            s1=(f'The {noun} is {"not " if n1 else ""}{t1}.' if lang=='en-en'
                                else f'这个{zh_noun}{"不是" if n1 else "是"}{t1}的。')
                            s2=f'The {noun} is {"not " if n2 else ""}{t2}.'
                            same_prop=int((first^n1)==(second^n2))
                            base=(f'Compare two alternative descriptions of the same {noun} at the same instant. Neither description is assumed to be true. For this task its status has exactly two mutually exclusive possibilities: {w0} and {w1}.\n'
                                  f'Sentence 1: {s1}\nTarget word 1: {t1}\nSentence 2: {s2}\nTarget word 2: {t2}\n')
                            for task in ('word','proposition'):
                                question=('Do the target words themselves have the same lexical meaning in these sentences?'
                                          if task=='word' else 'Do the two complete sentences describe the same status of the item?')
                                ident=f'{w0}:{lang}:first{first}:same{same_word}:neg{n1}{n2}:{task}'
                                rows.append(dict(trial_id=ident,item_id=ident,task='lexical_proposition',relation=task,
                                    condition=task,lexeme_family_id=w0,language_pair=lang,first=first,second=second,
                                    negation_1=n1,negation_2=n2,same_word=same_word,same_proposition=same_prop,
                                    gold_yes=same_word if task=='word' else same_prop,
                                    prompt=base+'\n'+question+'\nBegin with YES or NO and then give one short explanatory sentence.',
                                    label_provenance='agent-authored binary-domain semantics, no independent human review'))
    assert len(rows)==768 and len({r['trial_id'] for r in rows})==768
    return rows


if __name__=='__main__':
    p=Path(__file__).resolve().parents[1]/'experiments/stimuli/lexical_proposition_2026-10-13.jsonl'
    assert not p.exists()
    p.write_text(''.join(json.dumps(r,ensure_ascii=False)+'\n' for r in build()))
    print(p)
