import csv
import math

import pytest

from scripts.pilot_tanwar_gloss_margins import material,load_items,manifest,summarize


def write_source(tmp_path):
    words=["genial","blank"]
    ctx=tmp_path/"task3_en_de.csv"
    lex=tmp_path/"en_de_dataset.csv"
    cfields=["ID","en","de","type","lexical_category","high_en","low_en","high_de","low_de"]
    lfields=["ID","en","de","en_meaning","de_meaning","type"]
    with ctx.open("w",encoding="utf-8",newline="") as f:
        w=csv.DictWriter(f,fieldnames=cfields);w.writeheader()
        for i,x in enumerate(words,1):
            w.writerow(dict(ID=i,en=x,de=x,type="FALSE COGNATE",
                lexical_category="ADJ",high_en=f"A {x} guest arrived.",
                low_en=f"It was {x}.",high_de=f"Die Idee war {x}.",
                low_de=f"Das war {x}."))
    with lex.open("w",encoding="utf-8",newline="") as f:
        w=csv.DictWriter(f,fieldnames=lfields);w.writeheader()
        for i,x in enumerate(words,1):
            w.writerow(dict(ID=i,en=x,de=x,type="FALSE COGNATE",
                en_meaning="friendly and warm",de_meaning="clever and brilliant"))
    return ctx,lex


def test_crossfile_and_question_construction(tmp_path):
    ctx,lex=write_source(tmp_path)
    items=load_items(ctx,lex,["1","2"])
    m=manifest(items,["high"],["none","q1_host","q1_other"])
    assert len(m)==2*2*1*3*2
    none=next(x for x in m if x["source_id"]=="1" and x["host_language"]=="de"
         and x["cue"]=="none" and x["correct_as_a"])
    host=next(x for x in m if x["source_id"]=="1" and x["host_language"]=="de"
         and x["cue"]=="q1_host" and x["correct_as_a"])
    other=next(x for x in m if x["source_id"]=="1" and x["host_language"]=="de"
         and x["cue"]=="q1_other" and x["correct_as_a"])
    assert none["candidate_correct"]=="clever and brilliant"
    assert 'Die Idee war "genial".' in none["prompt"]
    assert "The quoted word is German" not in none["prompt"]
    assert "quoted word is German" in host["prompt"]
    assert "quoted word is English" in other["prompt"]
    assert none["candidate_correct"]==host["candidate_correct"]==other["candidate_correct"]
    assert len({a["prompt_sha256"] for a in (none,host,other)})==3


def test_compound_filter_requires_adjective(tmp_path):
    ctx,lex=write_source(tmp_path)
    contents=ctx.read_text().replace("ADJ","N",1)
    ctx.write_text(contents)
    with pytest.raises(ValueError,match="adjective-only"):
        load_items(ctx,lex,["1"])


def test_pair_average_and_missing_pair():
    base={"source_id":"1","host_language":"de","context_strength":"high",
          "cue":"none","form":"genial"}
    pair=[{**base,"correct_as_a":True,"correct_minus_foil_margin":1.0},
          {**base,"correct_as_a":False,"correct_minus_foil_margin":3.0}]
    res=summarize(pair)
    assert len(res)==1 and res[0]["mean_correct_minus_foil_margin"]==2.0
    assert res[0]["status"]=="EXPLORATORY_NOT_INFERENTIAL"
    with pytest.raises(ValueError,match="missing"):
        summarize(pair[:1])


def test_mask_count_validation():
    item={"id":"1","form":"genial","english_meaning":"friendly",
          "german_meaning":"clever",
          "contexts":{"high_en":"The <MASK> and <MASK> are here."}}
    with pytest.raises(ValueError,match="precisely one mask"):
        material(item,"en","high","none",True)
