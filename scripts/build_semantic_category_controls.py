"""Post-hoc task controls after v2's explicit air-conditioner classification failure."""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def build():
    items = []
    for noun, gold in [("空调设备", 0), ("电风扇", 0), ("冷空气", 1), ("空气流动", 1)]:
        family = hashlib.sha256(noun.encode()).hexdigest()[:20]
        for frame in ["negative_hot_room", "positive_notice"]:
            if frame == "negative_hot_room":
                context = f"这个房间没有{noun}，我觉得很热。"
                referent = "句中“没有”后提到的对象"
            else:
                context = f"她注意到这里的{noun}。"
                referent = "句中“注意到”的对象"
            question = "记录员按所指对象分组：设备组登记可制造、安装的机器；环境组记录空气本身的温度和流动。" + referent + "应归给哪一组？"
            items.append({
                "schema_version": "semantic-category-control-posthoc-v1",
                "item_id": f"category-control-v1:{family}:{frame}",
                "lexeme_family_id": family, "source_language": "zh",
                "context_revision": frame, "word_jp": None, "word_zh": noun,
                "target_word": noun, "context_original": context, "question": question,
                "options": ["设备组", "环境组"], "correct_index": gold,
                "variants": ["original"],
                "variant_prompts": {"original": "请阅读下面的中文句子并回答问题。\n" + context + "\n" + question},
                "review": {"reviewer_type": "single_root_agent_posthoc_not_independent_human",
                           "rationale": "Machine objects versus air/air motion, classified by referent whether present or absent.",
                           "limitation": "Two nominal frames are paired materials, not a pure negation manipulation; generic Chinese task control, not a cross-language sense test."},
                "provenance": {"source": "newly authored task control", "selection": "after inspecting v2 Llama explicit air-conditioner failures", "heldout": False},
            })
    return items


if __name__ == "__main__":
    path = ROOT / "data/processed/semantic_category_controls_v1.jsonl"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("".join(json.dumps(row, ensure_ascii=False) + "\n" for row in build()))
    print(path, hashlib.sha256(path.read_bytes()).hexdigest())
