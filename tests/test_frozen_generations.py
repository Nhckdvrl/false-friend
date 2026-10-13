from scripts.analyze_frozen_generations import parse_initial_answer


def test_natural_initial_answer_routes_and_mapping():
    assert parse_initial_answer('Die richtige Antwort ist A) Cedar.\nBecause...', [0,1])['choice'] == 0
    assert parse_initial_answer('Maple', [0,1])['choice'] == 1
    assert parse_initial_answer('B) Cedar', [1,0])['choice'] == 0
    assert parse_initial_answer('**A**', [1,0])['choice'] == 1


def test_conflicts_and_nonanswers_are_not_silently_correct():
    assert parse_initial_answer('A) Maple', [0,1])['parse_status'] == 'conflicting'
    assert parse_initial_answer('A bird is meant here.', [0,1])['choice'] is None
    assert parse_initial_answer('Either Cedar or Maple.', [0,1])['choice'] is None
    assert parse_initial_answer('', [0,1])['parse_status'] == 'empty'
