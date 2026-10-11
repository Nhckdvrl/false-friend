"""No-network tests of exact Tanwar Task3 prompt and same-item order controls."""
import csv

import pytest

from scripts.pilot_tanwar_prompt_order import (
    ORIGINAL_INSTRUCTION, build_manifest, make_stimulus, prompt_text
)


@pytest.fixture
def row():
    return {
        "ID":"7","en":"gift","de":"gift","type":"FALSE COGNATE",
        "lexical_category":"N",
        "high_en":"She received a wonderful <MASK> for her birthday.",
        "low_en":"It was a <MASK>.",
        "high_de":"Das Paket enthielt ein gefährliches <MASK>.",
        "low_de":"Es war ein <MASK>."
    }


def test_original_cross_question_prompt_exact_match(row):
    rec=prompt_text(row,l2="de",word_language="en",strength="high",variant="original")
    assert rec["prompt"] == ORIGINAL_INSTRUCTION.format(l1="English",l2="German") + "\n" + \
        'Das Paket enthielt ein gefährliches "gift".'
    assert rec["host_sentence_language"]=="de"
    assert rec["surface_identity"] is True


def test_order_swaps_only_question_semantics_not_sentence(row):
    a=prompt_text(row,l2="de",word_language="en",strength="high",variant="original")
    b=prompt_text(row,l2="de",word_language="en",strength="high",variant="meaning_first")
    c=prompt_text(row,l2="de",word_language="en",strength="high",variant="meaning_only")
    assert a["context"]==b["context"]==c["context"]
    assert "Q1. What is the language" in a["prompt"]
    assert "Q1. What is the meaning" in b["prompt"]
    assert "Q1." not in c["prompt"]
    assert '"gift"' in a["context"]


def test_exact_form_cross_matches_normal_sentence_but_source_differs(row):
    s_en,host1=make_stimulus(row,l2="de",word_language="en",strength="high")
    original_de=row["high_de"].replace("<MASK>",'"'+row["de"]+'"')
    assert s_en==original_de and host1=="de"


def test_missing_source_mask_rejected(row):
    row["high_de"]="Sentence without any target."
    with pytest.raises(ValueError,match="exactly one"):
        make_stimulus(row,l2="de",word_language="en",strength="high")


def test_manifest_no_model_nor_gold_instrument(tmp_path,row):
    p=tmp_path/"task3_en_de.csv"
    with p.open("w",newline="",encoding="utf-8") as f:
        cols=list(row)
        writer=csv.DictWriter(f,fieldnames=cols)
        writer.writeheader()
        writer.writerow(row)
    m=build_manifest(p,"de",limit=1,strength="low",
                     variants=["original","meaning_only"])
    assert len(m)==4
    assert {x["word_language_index"] for x in m}=={"en","de"}
    assert {x["prompt_variant"] for x in m}=={"original","meaning_only"}
    assert all("gold_label" not in x and "generated" not in x for x in m)
