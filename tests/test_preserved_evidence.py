"""Preserve original historical smoke data, not certify its scientific validity."""
import hashlib
import json
from pathlib import Path

import pytest

from scripts.analyze_gloss_order_bias import audit_scores

EVIDENCE = Path(__file__).resolve().parents[1] / 'evidence/2026-10-12-cpu-pilots'


def test_historical_run_files_match_recorded_digests():
    provenance = json.loads((EVIDENCE / 'provenance.json').read_text(encoding='utf-8'))
    assert provenance['status'] == 'HISTORICAL_INSTRUMENT_SMOKE_NOT_CONFIRMED_DISCOVERY'
    for run in provenance['runs']:
        content = (EVIDENCE / run['retained_file']).read_bytes()
        assert hashlib.sha256(content).hexdigest() == run['retained_sha256']
        assert len(json.loads(content)) == run['rows']
        assert run['model_sha'] == run['tokenizer_sha']


def test_recompute_previous_option_order_observations():
    provenance = json.loads((EVIDENCE / 'provenance.json').read_text(encoding='utf-8'))
    matrix = json.loads((EVIDENCE / 'score_matrix.json').read_text(encoding='utf-8'))
    rows = []
    for values in matrix:
        row = dict(zip(provenance['score_matrix_columns'], values))
        row['context_strength'] = provenance['score_common']['context_strength']
        row['form'] = provenance['score_common']['source_ids_to_forms'][row['source_id']]
        expected = row['logp_A'] - row['logp_B']
        if not row['correct_as_a']:
            expected = -expected
        assert expected == pytest.approx(row['correct_minus_foil_margin'], abs=1e-10)
        rows.append(row)
    result = audit_scores(rows)
    assert result['n_trials'] == 36
    assert result['n_pairs'] == 18
    assert result['n_sign_reversals'] == 7
    assert result['n_order_gaps_above_threshold'] == 14
    assert result['mean_abs_order_gap_nats'] == pytest.approx(3.905065006679959)
    assert len(provenance['score_prompt_sha256_in_row_order']) == len(matrix)
