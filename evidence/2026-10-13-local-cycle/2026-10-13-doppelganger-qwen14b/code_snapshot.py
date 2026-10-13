#!/usr/bin/env python3
"""Published Type-1 scoring plus explicitly separate access/output diagnostics.

Source code and data remain in ignored data/raw; no third-party corpus is vendored.
Full prompts, scores and generations are saved in an immutable run directory.
Uses an existing environment and cached weights; never downloads model weights.
"""
from __future__ import annotations

import argparse
import ast
from collections import Counter
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import subprocess
import time

SOURCE_SHA = "eb1c4f3f17403af238046bf218dc49643bc2e2e2"
PROTOCOL = "doppelganger-type1-access-v1"


def digest(value: str | bytes) -> str:
    return hashlib.sha256(value.encode() if isinstance(value, str) else value).hexdigest()


def author_functions(source: Path, name: str) -> dict:
    """Only the two inspected pure source functions, not the model runner."""
    tree = ast.parse((source / name).read_text())
    functions = [n for n in tree.body if isinstance(n, ast.FunctionDef)
                 and n.name in {"loadQADataset", "formatInput"}]
    scope: dict = {}
    exec(compile(ast.Module(body=functions, type_ignores=[]), name, "exec"), scope)
    return scope


def literal_dataset(path: Path) -> dict:
    tree = ast.parse(path.read_text())
    assignments = [n for n in tree.body if isinstance(n, ast.Assign)
                   and any(isinstance(t, ast.Name) and t.id == "dataset" for t in n.targets)]
    if len(assignments) != 1:
        raise ValueError(f"Expected one literal dataset: {path}")
    return ast.literal_eval(assignments[0].value)


def family_id(jp: str, zh: str) -> str:
    return digest(jp.strip() + "\u241f" + zh.strip())[:20]


def records(source: Path) -> list[dict]:
    wm = author_functions(source, "calc_ppl_meaning.py")
    wmc = author_functions(source, "calc_ppl_meaning_context.py")
    translation = author_functions(source, "calc_ppl_translation.py")
    result = []
    for lang in ("jp", "zh"):
        other = "zh" if lang == "jp" else "jp"
        path = source / "cognate_fixed" / lang / "homographs.txt"
        isolated = wm["loadQADataset"](path, "homographs", lang)
        contextual = wmc["loadQADataset"](path, "homographs", lang)
        examples = literal_dataset(source / "questions" / f"{lang}_{other}" / "homographs.py")
        for task in ("meaning", "context", "translation"):
            keys = list(isolated if task == "meaning" else examples)
            for i, key in enumerate(keys):
                entry = isolated[key] if task == "meaning" else contextual[key]
                # Minimal repair for the missing own-language field in author WM loader.
                word = key if task == "meaning" else entry[f"word_{'ja' if lang == 'jp' else 'zh'}"]
                if task == "meaning":
                    jp_word, zh_word = ((key, entry["word_zh"]) if lang == "jp"
                                        else (entry["word_ja"], key))
                else:
                    jp_word, zh_word = entry["word_ja"], entry["word_zh"]
                sentence = "" if task == "meaning" else examples[key]["target-sentence"]
                if task == "translation":
                    candidates = [examples[key][k] for k in ("correct", "wrong1", "wrong2", "wrong3")]
                    formatter = lambda c: translation["formatInput"](sentence, c, other)
                else:
                    mapping = isolated if task == "meaning" else contextual
                    nxt = mapping[keys[(i + 1) % len(keys)]]
                    candidates = [entry[f"mean_{lang}"], entry[f"mean_{other}"],
                                  nxt["mean_zh"], nxt["mean_jp"]]
                    candidates = [c.replace("\n", "") for c in candidates]
                    if task == "meaning":
                        formatter = lambda c: wm["formatInput"](word, c, lang)
                    else:
                        formatter = lambda c: wmc["formatInput"](word, c, sentence, lang)
                # Recover exact source prefix/suffix without substring ambiguity.
                marker = "__CANDIDATE_BOUNDARY_20261013__"
                template = formatter(marker)
                prefix, suffix = template.split(marker)
                texts = [formatter(c) for c in candidates]
                assert texts == [prefix + c + suffix for c in candidates]
                fam = family_id(jp_word, zh_word)
                result.append({
                    "item_id": f"type1:{lang}:{task}:{fam}", "lexeme_family_id": fam,
                    "sense_pair_id": f"type1:{fam}", "context_family_id": f"type1:{fam}:{lang}",
                    "source_key": key, "word_jp": jp_word, "word_zh": zh_word,
                    "source_language": lang, "target_language": other if task == "translation" else lang,
                    "task": task, "type": 1, "source_label": 0, "source_index": i,
                    "sentence": sentence, "candidates": candidates,
                    "prefix": prefix, "suffix": suffix, "texts": texts,
                    "source_label_provenance": "published benchmark; not independent new review",
                })
    return result


def selected_families(items: list[dict], count: int) -> list[str]:
    families = {r["lexeme_family_id"] for r in items}
    return sorted(families, key=lambda f: digest("20261013:" + f))[:count]


def null_prefix(lang: str, task: str) -> tuple[str, str]:
    if task == "translation":
        return (("日本語訳は「", "」です。") if lang == "jp" else ("中文翻译是\"", "\"."))
    return (("この単語の意味は「", "」です。") if lang == "jp" else ("这个词的意思是“", "”."))


def loss_parts(losses: list[float], offsets: list[tuple[int, int]], start: int, end: int) -> dict:
    if len(losses) != len(offsets) - 1 or end <= start:
        raise ValueError("Shifted losses or candidate boundaries invalid")
    parts = {k: {"nll_sum": 0.0, "tokens": 0} for k in ("prefix", "candidate", "suffix")}
    crossings = 0
    for loss, (a, b) in zip(losses, offsets[1:]):
        part = "prefix" if b <= start else "suffix" if a >= end else "candidate"
        parts[part]["nll_sum"] += loss
        parts[part]["tokens"] += 1
        crossings += int(a < start < b or a < end < b)
    total = sum(losses)
    return {"full_nll_sum": total, "full_tokens": len(losses),
            "full_nll_mean": total / len(losses), "parts": parts,
            "boundary_crossing_tokens": crossings}


def score_texts(model, tokenizer, specifications: list[tuple[str, str, str]], batch_size: int) -> dict:
    import torch
    import torch.nn.functional as F
    unique = list(dict.fromkeys(specifications))
    encoded = []
    for prefix, candidate, suffix in unique:
        text = prefix + candidate + suffix
        tok = tokenizer(text, return_offsets_mapping=True)
        encoded.append((len(tok["input_ids"]), (prefix, candidate, suffix), tok))
    encoded.sort(key=lambda x: x[0])
    result = {}
    for b in range(0, len(encoded), batch_size):
        batch = encoded[b:b + batch_size]
        longest = batch[-1][0]
        ids = torch.full((len(batch), longest), tokenizer.pad_token_id, dtype=torch.long, device=model.device)
        attention = torch.zeros_like(ids)
        for i, (length, _, tok) in enumerate(batch):
            ids[i, :length] = torch.tensor(tok["input_ids"], device=model.device)
            attention[i, :length] = 1
        with torch.inference_mode():
            logits = model(input_ids=ids, attention_mask=attention, use_cache=False).logits
            losses = F.cross_entropy(logits[:, :-1].float().reshape(-1, logits.shape[-1]),
                                     ids[:, 1:].reshape(-1), reduction="none").reshape(len(batch), -1)
            losses = losses.cpu().tolist()
        for i, (length, spec, tok) in enumerate(batch):
            prefix, candidate, _ = spec
            result[spec] = loss_parts(losses[i][:length - 1], tok["offset_mapping"], len(prefix), len(prefix + candidate))
        del logits
        if b == 0 or (b // batch_size) % 40 == 0 or b + batch_size >= len(encoded):
            print(f"candidate forwards {min(b + batch_size, len(encoded))}/{len(encoded)}", flush=True)
    return result


def chat_prompt(record: dict, order: list[int]) -> str:
    lang, task = record["source_language"], record["task"]
    word = record[f"word_{lang}"]
    if lang == "jp":
        question = {
            "meaning": f"日本語の単語「{word}」の意味はどれですか？",
            "context": f"日本語の文「{record['sentence']}」内の「{word}」の意味はどれですか？",
            "translation": f"次の日本語の文の適切な中国語訳はどれですか？\n{record['sentence']}",
        }[task]
        instruction = "正解の選択肢の記号（A、B、C、D）のみを答えてください。"
    else:
        question = {
            "meaning": f"中文词语“{word}”的含义是哪一项？",
            "context": f"中文句子“{record['sentence']}”中“{word}”的含义是哪一项？",
            "translation": f"下面中文句子恰当的日语翻译是哪一项？\n{record['sentence']}",
        }[task]
        instruction = "只回答正确选项的字母（A、B、C、D）。"
    return question + "\n" + "\n".join(f"{label}) {record['candidates'][idx]}" for label, idx in zip("ABCD", order)) + "\n" + instruction


def score_labels(model, tokenizer, specifications: list[dict], batch_size: int) -> list[dict]:
    import torch
    encoded = []
    for r in specifications:
        rendered = tokenizer.apply_chat_template([{"role": "user", "content": r["prompt"]}],
                                                  tokenize=False, add_generation_prompt=True)
        ids = tokenizer.encode(rendered, add_special_tokens=False)
        label_ids = []
        for label in "ABCD":
            full = tokenizer.encode(rendered + label, add_special_tokens=False)
            if full[:-1] != ids or len(full) != len(ids) + 1:
                raise ValueError("Labels are not a unique single-token continuation")
            label_ids.append(full[-1])
        encoded.append((r, ids, label_ids, rendered))
    result = []
    for b in range(0, len(encoded), batch_size):
        batch = encoded[b:b + batch_size]
        longest = max(len(x[1]) for x in batch)
        ids = torch.full((len(batch), longest), tokenizer.pad_token_id, dtype=torch.long, device=model.device)
        attention = torch.zeros_like(ids)
        for i, (_, tokens, _, _) in enumerate(batch):
            ids[i, :len(tokens)] = torch.tensor(tokens, device=model.device)
            attention[i, :len(tokens)] = 1
        with torch.inference_mode():
            outputs = model(input_ids=ids, attention_mask=attention, use_cache=False)
            final = outputs.logits[torch.arange(len(batch), device=model.device),
                                  torch.tensor([len(x[1]) - 1 for x in batch], device=model.device)].float()
            logps = torch.log_softmax(final, dim=-1)
        for i, (r, tokens, labels, rendered) in enumerate(batch):
            result.append({**r, "label_token_ids": labels, "label_logps": logps[i, labels].cpu().tolist(),
                           "unrestricted_argmax_token": int(final[i].argmax()),
                           "rendered_prompt": rendered, "rendered_prompt_sha256": digest(rendered),
                           "input_tokens": len(tokens), "status": "LABEL_SCORED_NEW_DIAGNOSTIC"})
        del outputs
        if b == 0 or (b // batch_size) % 40 == 0 or b + batch_size >= len(encoded):
            print(f"label forwards {min(b + batch_size, len(encoded))}/{len(encoded)}", flush=True)
    return result


def free_prompt(record: dict) -> str:
    lang, task = record["source_language"], record["task"]
    word = record[f"word_{lang}"]
    if lang == "jp":
        return {"meaning": f"日本語の単語「{word}」の意味を日本語で短く説明してください。",
                "context": f"次の日本語の文で使われる「{word}」の意味を日本語で短く説明してください。\n{record['sentence']}",
                "translation": f"次の日本語の文を中国語に翻訳してください。訳文だけを答えてください。\n{record['sentence']}"}[task]
    return {"meaning": f"请用中文简短解释中文词语“{word}”的含义。",
            "context": f"请用中文简短解释下面中文句子中“{word}”的含义。\n{record['sentence']}",
            "translation": f"请将下面中文句子翻译为日语。只回答译文。\n{record['sentence']}"}[task]


def generate_records(model, tokenizer, specifications: list[dict], batch_size: int, max_tokens: int) -> list[dict]:
    import torch
    tokenizer.padding_side = "left"
    result = []
    for b in range(0, len(specifications), batch_size):
        batch = specifications[b:b + batch_size]
        rendered = [tokenizer.apply_chat_template([{"role": "user", "content": r["prompt"]}],
                                                  tokenize=False, add_generation_prompt=True) for r in batch]
        inputs = tokenizer(rendered, padding=True, return_tensors="pt", add_special_tokens=False).to(model.device)
        with torch.inference_mode():
            outputs = model.generate(**inputs, do_sample=False, max_new_tokens=max_tokens,
                                     pad_token_id=tokenizer.pad_token_id)
        for i, r in enumerate(batch):
            new = outputs[i, inputs.input_ids.shape[1]:].cpu().tolist()
            eos = model.generation_config.eos_token_id
            eos = [eos] if isinstance(eos, int) else (eos or [])
            stop = next((j for j, t in enumerate(new) if t in eos), len(new))
            generated_ids = new[:stop + 1] if stop < len(new) else new
            result.append({**r, "generated": tokenizer.decode(generated_ids, skip_special_tokens=True),
                           "generated_token_ids": generated_ids, "generated_tokens": len(generated_ids),
                           "hit_token_limit": stop == len(new) and len(new) >= max_tokens,
                           "rendered_prompt": rendered[i], "rendered_prompt_sha256": digest(rendered[i]),
                           "status": "GENERATED_UNSCORED"})
        print(f"generations {min(b + batch_size, len(specifications))}/{len(specifications)}", flush=True)
    return result


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--source", type=Path, required=True)
    ap.add_argument("--model-path", type=Path, required=True)
    ap.add_argument("--model-id", required=True)
    ap.add_argument("--output", type=Path, required=True)
    ap.add_argument("--batch-size", type=int, default=16)
    ap.add_argument("--chat-families", type=int, default=96)
    ap.add_argument("--generation-families", type=int, default=24)
    ap.add_argument("--max-new-tokens", type=int, default=128)
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()
    sha = subprocess.check_output(["git", "-C", str(a.source), "rev-parse", "HEAD"], text=True).strip()
    if sha != SOURCE_SHA:
        raise ValueError(f"Unreviewed source revision {sha}")
    items = records(a.source)
    chat_families = selected_families(items, a.chat_families)
    generation_families = chat_families[:a.generation_families]
    chat = []
    generations = []
    for r in items:
        if r["lexeme_family_id"] in chat_families:
            for rotation in range(4):
                order = [(i + rotation) % 4 for i in range(4)]
                chat.append({**r, "rotation": rotation, "content_order": order, "prompt": chat_prompt(r, order)})
        if r["lexeme_family_id"] in generation_families:
            generations.append({**r, "prompt": free_prompt(r)})
    a.output.mkdir(parents=True, exist_ok=False)
    root = Path(__file__).resolve().parents[1]
    source_files = sorted(set(a.source.glob("calc_ppl*.py")) | set(a.source.glob("cognate_fixed/*/homographs.txt"))
                          | set(a.source.glob("questions/*/homographs.py")))
    manifest = {
        "protocol_revision": PROTOCOL, "source_repository": "https://github.com/0017-alt/Doppelganger-JC",
        "source_sha": sha, "source_files_sha256": {str(p.relative_to(a.source)): digest(p.read_bytes()) for p in source_files},
        "code_git_sha": subprocess.check_output(["git", "-C", str(root), "rev-parse", "HEAD"], text=True).strip(),
        "code_file_sha256": digest(Path(__file__).read_bytes()), "dirty_code": True,
        "model_id": a.model_id, "model_revision": a.model_path.name, "tokenizer_revision": a.model_path.name,
        "model_path": str(a.model_path), "selection_seed": "sha256(20261013:family_id)",
        "sample_families": chat_families, "generation_families": generation_families,
        "sample_unit": "JP/ZH lexical pair; directions/tasks/rotations are repeated measures",
        "task_counts": dict(Counter(r["source_language"] + ":" + r["task"] for r in items)),
        "candidate_items": len(items), "chat_trials": len(chat), "generations": len(generations),
        "batch_size": a.batch_size, "max_new_tokens": a.max_new_tokens,
        "status": "DRY_RUN" if a.dry_run else "RUNNING", "started_utc": datetime.now(timezone.utc).isoformat(),
        "deviations": ["WM missing own-language word field repaired with own-language dictionary key",
                       "Llama uses NousResearch mirror when requested; original weight identity not certified",
                       "batched SDPA inference; source used sequential inference and unspecified library versions",
                       "conditional/null-input/chat/generation are NEW diagnostics, not original metric"],
        "budget": "2 independent local GPUs, no training or paid inference; no model download",
    }
    (a.output / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2))
    (a.output / "inputs.jsonl").write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in items))
    if a.dry_run:
        print(json.dumps(manifest, ensure_ascii=False, indent=2))
        return
    import platform
    import torch
    import transformers
    from transformers import AutoModelForCausalLM, AutoTokenizer
    started = time.monotonic()
    torch.set_num_threads(4)
    torch.manual_seed(20261013)
    tokenizer = AutoTokenizer.from_pretrained(a.model_path, local_files_only=True, trust_remote_code=False)
    if tokenizer.pad_token_id is None:
        tokenizer.pad_token = tokenizer.eos_token
    model = AutoModelForCausalLM.from_pretrained(a.model_path, local_files_only=True, trust_remote_code=False,
                                               torch_dtype=torch.bfloat16, device_map={"": "cuda:0"},
                                               attn_implementation="sdpa").eval()
    manifest.update({"environment": {"python": platform.python_version(), "torch": torch.__version__,
                                     "transformers": transformers.__version__, "cuda": torch.version.cuda},
                     "gpu": torch.cuda.get_device_name(), "cuda_visible_devices": os.getenv("CUDA_VISIBLE_DEVICES"),
                     "chat_template_sha256": digest(tokenizer.chat_template or "")})
    (a.output / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2))
    specs = [(r["prefix"], c, r["suffix"]) for r in items for c in r["candidates"]]
    for r in items:
        p, s = null_prefix(r["target_language"], r["task"])
        specs.extend((p, c, s) for c in r["candidates"])
    losses = score_texts(model, tokenizer, specs, a.batch_size)
    # Compare batched token sums to the library's original scalar loss.
    ref = items[0]
    inputs = tokenizer(ref["texts"][0], return_tensors="pt").to(model.device)
    with torch.inference_mode():
        library_loss = model(**inputs, labels=inputs.input_ids).loss.item()
    ours = losses[(ref["prefix"], ref["candidates"][0], ref["suffix"])]["full_nll_mean"]
    manifest["scalar_loss_verification"] = {"library_loss": library_loss, "batched_loss": ours, "abs_error": abs(library_loss - ours)}
    if abs(library_loss - ours) > 0.002:
        raise ValueError("Batched scoring differs from original library loss")
    with (a.output / "trials.jsonl").open("w") as out:
        for r in items:
            p, s = null_prefix(r["target_language"], r["task"])
            scores = [losses[(r["prefix"], c, r["suffix"])] for c in r["candidates"]]
            priors = [losses[(p, c, s)] for c in r["candidates"]]
            out.write(json.dumps({**r, "scores": scores, "null_input_scores": priors,
                                  "status": "SOURCE_PPL_AND_NEW_DIAGNOSTICS"}, ensure_ascii=False) + "\n")
    print("Published-task candidate stage complete", flush=True)
    with (a.output / "chat_trials.jsonl").open("w") as out:
        for r in score_labels(model, tokenizer, chat, a.batch_size):
            out.write(json.dumps(r, ensure_ascii=False) + "\n")
    with (a.output / "generations.jsonl").open("w") as out:
        for r in generate_records(model, tokenizer, generations, min(8, a.batch_size), a.max_new_tokens):
            out.write(json.dumps(r, ensure_ascii=False) + "\n")
    manifest.update({"status": "COMPLETE", "finished_utc": datetime.now(timezone.utc).isoformat(),
                     "elapsed_seconds": time.monotonic() - started,
                     "peak_allocated_gb": torch.cuda.max_memory_allocated() / 1e9})
    (a.output / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2))
    print(f"Completed {a.output} in {manifest['elapsed_seconds']:.1f}s", flush=True)


if __name__ == "__main__":
    main()
