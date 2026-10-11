import csv

import pytest

from scripts.audit_tanwar_identifiability import audit_one, insert


def write_source(path, en, de, typ):
    cols = ["ID", "en", "de", "type", "lexical_category",
            "low_en", "high_en", "low_de", "high_de"]
    with path.open("w", encoding="utf-8", newline="") as fp:
        writer = csv.DictWriter(fp, fieldnames=cols)
        writer.writeheader()
        writer.writerow({
            "ID":"1", "en":en, "de":de, "type":typ, "lexical_category":"N",
            "low_en":"The <MASK> appeared.",
            "high_en":"The character was a <MASK>.",
            "low_de":"Der <MASK> war dort.",
            "high_de":"Die Person sah den <MASK> auf dem Foto.",
        })


def test_insert_one_mask():
    assert insert("The <MASK> appeared.", "angel") == 'The "angel" appeared.'
    with pytest.raises(ValueError, match="exactly one"):
        insert("The <MASK> and <MASK>.", "x")
    with pytest.raises(ValueError, match="exactly one"):
        insert("No mask!", "x")


def test_identical_form_has_four_sentence_equivalences(tmp_path):
    f = tmp_path / "task3_en_de.csv"
    write_source(f, "gift", "gift", "FALSE COGNATE")
    r = audit_one(f, "de")
    assert r["counts"]["exact_type_FALSE COGNATE"] == 1
    assert r["counts"]["exact_ff_german_noun_lowercase_risk"] == 1
    assert r["counts"]["sentence_observational_equivalences"] == 4
    assert r["counts"]["host_and_strength_comparisons"] == 4


def test_case_difference_does_not_pass_strict_equivalence(tmp_path):
    f = tmp_path / "task3_en_de.csv"
    write_source(f, "gift", "Gift", "FALSE COGNATE")
    r = audit_one(f, "de")
    assert r["counts"]["case_only_forms"] == 1
    assert r["counts"].get("sentence_observational_equivalences", 0) == 0


def test_different_form_is_observably_different(tmp_path):
    f = tmp_path / "task3_en_de.csv"
    write_source(f, "sensible", "sensibel", "FALSE COGNATE")
    r = audit_one(f, "de")
    assert r["counts"].get("sentence_observational_equivalences", 0) == 0
