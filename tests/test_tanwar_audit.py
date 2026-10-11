import csv

import pytest

from scripts.audit_tanwar_baseline import audit


def test_context_mask_audit(tmp_path):
    path = tmp_path / "task3_en_de.csv"
    names = ["ID", "en", "de", "type", "lexical_category", "low_en", "high_en", "low_de", "high_de"]
    with path.open("w", newline="", encoding="utf-8") as fp:
        writer = csv.DictWriter(fp, fieldnames=names)
        writer.writeheader()
        writer.writerow({
            "ID": 1, "en": "angel", "de": "Angel", "type": "FALSE COGNATE",
            "lexical_category": "N", "low_en": "The <MASK> is here.",
            "high_en": "The <MASK> helped us.",
            "low_de": "Der <MASK> liegt da.", "high_de": "Er warf die Angelrute, und der Angel liegt dort."
        })
    out = audit(path, "de")
    assert out["rows"] == 1
    assert out["missing_mask_rows"] == 1
    assert out["type_counts"]["FALSE COGNATE"] == 1


def test_schema_fail_fast(tmp_path):
    file = tmp_path / "task3_en_de.csv"
    file.write_text("ID,en,de\n1,a,b\n", encoding="utf-8")
    with pytest.raises(ValueError, match="missing"):
        audit(file, "de")
