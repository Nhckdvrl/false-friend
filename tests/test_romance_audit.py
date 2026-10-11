import csv
from pathlib import Path

import pytest

from scripts.audit_romance_wic import InputError, audit_files, is_whole_form, load_tsv


def write(path: Path, rows: list[dict]) -> Path:
    fields = ["W1", "C1", "P1", "W2", "C2", "P2", "R", "POS"]
    with path.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, delimiter="\t", fieldnames=fields)
        w.writeheader()
        w.writerows(rows)
    return path


def entry(w1, c1, w2, c2, r, pos="N"):
    return dict(W1=w1, C1=c1, P1="1", W2=w2, C2=c2, P2="2", R=r, POS=pos)


def test_exact_surface_not_lemma_inflection_or_case():
    assert is_whole_form("azar", "¡Qué azar!")
    assert not is_whole_form("azar", "azaroso")
    assert not is_whole_form("azar", "Azar")
    assert is_whole_form("copo", "Veio um copo.")
    assert not is_whole_form("copo", "vieram copos.")


def test_source_audit_counts_and_duplicates(tmp_path):
    a = write(tmp_path / "auto-es-pt.tsv", [
        entry("azar", "O azar chegou.", "azar", "Juego de azar.", "0"),
        entry("azar", "O azar chegou.", "azar", "Juego de azar.", "0"),
        entry("copo", "Os copos caíram.", "copo", "O copo caiu.", "0"),
        entry("voto", "O voto vale.", "voto", "El voto vale.", "1"),
        entry("acceso", "El acceso es fácil.", "aceso", "A luz está acesa.", "0")
    ])
    b = write(tmp_path / "human-es-pt.tsv", [
        entry("azar", "O azar não veio.", "azar", "Juego de azar.", "0"),
    ])
    out = audit_files([a, b])
    assert out["totals"]["rows"] == 6
    assert out["totals"]["exact_lemma"] == 5
    assert out["totals"]["exact_lemma_ff"] == 4
    assert out["totals"]["context_ff"] == 3
    assert out["totals"]["context_same_sense"] == 1
    assert out["unique_candidate_language_pair_form"] == 1
    assert out["same_pair_form_label_duplicate_groups"] == 1
    assert not out["candidate_manifest"][0]["annotation_verified_for_new_experiment"]


def test_invalid_label_rejected(tmp_path):
    p = write(tmp_path / "human-es-pt.tsv", [entry("a", "a", "a", "a", "?")])
    with pytest.raises(InputError, match="R must"):
        load_tsv(p)


def test_missing_fields_rejected(tmp_path):
    p = tmp_path / "small.tsv"
    p.write_text("W1\tR\nazar\t0\n", encoding="utf-8")
    with pytest.raises(InputError, match="missing columns"):
        load_tsv(p)
