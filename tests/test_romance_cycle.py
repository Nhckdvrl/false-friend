from collections import Counter, defaultdict
from scripts.analyze_romance_cycle import parse_answer, explicit_label
from scripts.build_relation_orthogonal import build
from scripts.build_lexical_proposition import build as build_proposition
from scripts.build_scope_followup import build as build_scope
import re


def test_strict_opening_answer_not_reason_or_substring():
    assert parse_answer('Label: YES\nReason: Shared meaning.','romance_wic')==1
    assert parse_answer('**Label:** NO\nReason: Not shared.','romance_wic')==0
    assert parse_answer('They are similar. Label: YES','romance_wic') is None
    assert parse_answer('Label: Nobody knows.','romance_wic') is None
    assert parse_answer('**NO**, they are different people.','orthogonal_relation')==0
    assert parse_answer('One could answer YES.','orthogonal_relation') is None
    assert explicit_label("Let us compare.\nLabel: NO\nReason: Yes would be wrong.")==0
    assert explicit_label('Example: Label: YES\nLabel: NO')==0
    assert explicit_label('Label: YES\nLabel: NO') is None
    assert explicit_label('Reason: They are different.') is None


def test_orthogonal_gold_and_polarity_independent_factors():
    rows=build();groups=defaultdict(list)
    for r in rows:
        groups[(r['lexeme_family_id'],r['language_pair'],r['same_meaning'],r['same_person'],r['relation'])].append(r)
    assert len(groups)==384
    assert Counter(r['gold_yes'] for r in rows)=={0:384,1:384}
    for rr in groups.values():
        assert len(rr)==2 and {r['gold_yes'] for r in rr}=={0,1}
        pos=next(r for r in rr if r['polarity']=='same')
        assert pos['gold_yes']==pos['same_meaning' if pos['relation']=='meaning' else 'same_person']
    # A change of person must not change the lexical answer, and vice versa.
    lexical=defaultdict(set);personal=defaultdict(set)
    for r in rows:
        if r['relation']=='meaning':
            lexical[(r['lexeme_family_id'],r['language_pair'],r['same_meaning'],r['polarity'])].add(r['gold_yes'])
        else:
            personal[(r['lexeme_family_id'],r['language_pair'],r['same_person'],r['polarity'])].add(r['gold_yes'])
    assert all(len(v)==1 for v in list(lexical.values())+list(personal.values()))


def test_negation_changes_proposition_but_not_word_gold():
    rr=build_proposition()
    groups=defaultdict(dict)
    for r in rr:
        groups[r['trial_id'].rsplit(':',1)[0]][r['relation']]=r
    assert len(groups)==384
    for d in groups.values():
        w,p=d['word'],d['proposition']
        assert w['gold_yes']==int(w['first']==w['second'])
        assert (w['gold_yes']!=p['gold_yes'])==(w['negation_1']!=w['negation_2'])


def test_scope_only_changes_markup_and_gold_tracks_boundary():
    rr=build_scope();index={r['trial_id']:r for r in rr}
    assert len(rr)==864
    assert {r['lexeme_family_id'] for r in rr if r['split']=='explored'}.isdisjoint(
        {r['lexeme_family_id'] for r in rr if r['split']=='new_family'})
    for w in rr:
        if w['condition']!='word':continue
        p=index[w['trial_id'].rsplit(':',1)[0]+':predicate']
        strip=lambda s:re.sub(r'</?target>','',s)
        assert strip(w['prompt'])==strip(p['prompt'])
        assert (w['gold_yes']!=p['gold_yes'])==(w['negation_1']!=w['negation_2'])
        if w['negation_1']==w['negation_2']==0:
            assert w['prompt']==p['prompt']
