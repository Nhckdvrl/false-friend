from scripts.run_am2ico_target_binding import select_items, build_trials, bare
from scripts.run_am2ico_criterion_followup import build_trials as criterion_trials


def test_literal_tsv_quotes_preserve_rows_and_pair_intervention(tmp_path):
    # A literal unmatched quote is corpus content, not a multiline CSV field.
    for language in ['de','zh','ja']:
        folder=tmp_path/'data'/language;folder.mkdir(parents=True)
        (folder/'train.tsv').write_text('context1\tcontext2\tlabel\n'
            '"<word>wolf</word> and dog\t<word>wolf</word> and dog\tT\n'
            '"<word>wolf</word> and dog\twolf and <word>dog</word>\tF\n')
    items,audit=select_items(tmp_path,count=1)
    assert len(items)==6 and all(a['source_rows']==2 for a in audit.values())
    assert [r['source_line'] for r in items]==[2,3]*3
    for pos,neg in zip(items[::2],items[1::2]):
        assert list(map(bare,pos['contexts']))==list(map(bare,neg['contexts']))
        assert pos['changed_side']==1
    trials=build_trials(items,{})
    assert len(trials)==24
    for r in trials:
        assert (r['correct_index'] is None)==(r['representation']=='target_only')
        assert r['original_label_index']==(0 if r['source_label']=='T' else 1)
    followup=criterion_trials(trials)
    assert len(followup)==24
    for row in followup:
        original=next(r for r in trials if r['item_id']==row['item_id'] and r['rotation']==row['rotation'] and r['representation']=='full')
        assert row['contexts']==original['contexts']
        assert row['content_order']==original['content_order'] and row['correct_index']==original['correct_index']
        assert row['prompt'].split('\nDo the expressions')[0]==original['prompt'].split('\nDo the expressions')[0]
