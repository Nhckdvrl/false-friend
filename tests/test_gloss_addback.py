from scripts.run_am2ico_gloss_addback import build_trials
from scripts.analyze_gloss_addback import parse_yes_no
from scripts.run_am2ico_target_restatement import build_specs


def test_natural_answer_format_and_no_explanation_inference():
    assert parse_yes_no('**Yes**. Both refer to a boat.') == 'yes'
    assert parse_yes_no('Answer: No\n\nDifferent senses.') == 'no'
    assert parse_yes_no('**Answer:** Yes\n\n**Explanation:** Same sense.') == 'yes'
    assert parse_yes_no('The answer could be Yes, but it is ambiguous.') is None
    assert parse_yes_no('Nobody knows.') is None


def test_gloss_strings_fixed_and_semantic_mapping_tracks_question_polarity():
    item={'item_id':'x:T','pair_id':'x','source_label':'T','language':'de','targets':['Boot','boat'],
          'contexts':['Das <word>Boot</word> schwimmt.','A <word>boat</word> floats.']}
    outputs=[{**item,'generation_task':'joint_relation'},
             {**item,'generation_task':'independent_referent','side':0,'generated':'A watercraft.','hit_token_limit':False},
             {**item,'generation_task':'independent_referent','side':1,'generated':'A vessel for travelling on water.','hit_token_limit':False}]
    trials=build_trials([item],outputs,{})
    assert len(trials)==6
    assert len({tuple(r['gloss_hashes']) for r in trials})==1
    for r in trials:
        assert r['correct_index']==0
        expected_yes=(r['polarity']=='same')
        assert (r['content_order'][0]==r['correct_index'])==expected_yes
    only=next(r for r in trials if r['representation']=='gloss_only')
    add=next(r for r in trials if r['representation']=='raw_plus_gloss')
    assert only['glosses']==add['glosses']
    assert item['contexts'][0] not in only['prompt'] and item['contexts'][0] in add['prompt']
    corrected=build_specs(trials)
    assert len(corrected)==4
    for r in corrected:
        ref=next(t for t in trials if t['representation']=='gloss_only' and t['polarity']==r['polarity'])
        assert 'Target expression 1 (German): Boot' in r['prompt']
        assert item['contexts'][0] in r['prompt']
        if r['representation']=='raw_targets_gloss':
            assert r['prompt'].endswith(ref['prompt'])
        else:
            assert 'Independent description' not in r['prompt']
