from scripts.run_doppelganger_diagnostics import loss_parts, family_id, selected_families


def test_shifted_loss_decomposition_handles_boundary_tokens():
    result = loss_parts([1.0, 2.0, 3.0, 4.0], [(0, 0), (0, 3), (3, 5), (5, 8), (8, 9)], 4, 8)
    assert result["parts"]["prefix"] == {"nll_sum": 1.0, "tokens": 1}
    assert result["parts"]["candidate"] == {"nll_sum": 5.0, "tokens": 2}
    assert result["parts"]["suffix"] == {"nll_sum": 4.0, "tokens": 1}
    assert result["full_nll_mean"] == 2.5
    assert result["boundary_crossing_tokens"] == 1


def test_sampling_uses_families_not_repeated_measure_rows():
    families = [family_id("手紙", "手纸"), family_id("先生", "先生"), family_id("本", "本")]
    items = [{"lexeme_family_id": f} for f in families]
    assert selected_families(items, 2) == selected_families(items * 9, 2)
    assert len(set(selected_families(items, 2))) == 2
