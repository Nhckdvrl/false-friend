#!/usr/bin/env python3
"""Stream a frozen research JSONL through a cached model, preserving every response."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import platform
import time
import traceback

try:
    from scripts.run_doppelganger_diagnostics import generate_records
except ModuleNotFoundError:
    from run_doppelganger_diagnostics import generate_records


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--specs', type=Path, required=True)
    ap.add_argument('--model-path', required=True)
    ap.add_argument('--model-id', required=True)
    ap.add_argument('--output', type=Path, required=True)
    ap.add_argument('--batch-size', type=int, default=16)
    ap.add_argument('--max-new-tokens', type=int, default=128)
    a = ap.parse_args()
    specs = [json.loads(x) for x in a.specs.read_text().splitlines()]
    assert len({r['trial_id'] for r in specs}) == len(specs)
    kwargs = {'enable_thinking': False} if 'Qwen3-' in a.model_id else {}
    specs = [{**r, 'chat_template_kwargs': kwargs} for r in specs]
    a.output.mkdir(parents=True, exist_ok=False)
    manifest = dict(status='RUNNING', started_utc=datetime.now(timezone.utc).isoformat(),
        host=platform.node(), model_id=a.model_id, model_path=a.model_path,
        model_revision=Path(a.model_path).name, tokenizer_revision=Path(a.model_path).name,
        specs_path=str(a.specs.resolve()), specs_sha256=sha(a.specs), n_generations=len(specs),
        batch_size=a.batch_size, max_new_tokens=a.max_new_tokens, seed=20261013,
        chat_template_kwargs=kwargs, dtype='bfloat16', attention='sdpa', do_sample=False,
        cuda_visible_devices=os.getenv('CUDA_VISIBLE_DEVICES'), code_sha256=sha(__file__),
        generation_code_sha256=sha(generate_records.__code__.co_filename), completed=0)
    def save():
        (a.output/'manifest.json').write_text(json.dumps(manifest, indent=2, ensure_ascii=False))
    save()
    (a.output/'generation_specs.jsonl').write_text(''.join(json.dumps(r,ensure_ascii=False)+'\n' for r in specs))
    (a.output/'code_snapshot.py').write_bytes(Path(__file__).read_bytes())
    (a.output/'generation_code_snapshot.py').write_bytes(Path(generate_records.__code__.co_filename).read_bytes())
    start = time.monotonic()
    try:
        import torch
        import transformers
        from transformers import AutoConfig, AutoTokenizer, AutoModelForCausalLM, Gemma3ForConditionalGeneration
        torch.set_num_threads(4)
        torch.manual_seed(manifest['seed'])
        tokenizer = AutoTokenizer.from_pretrained(a.model_path, local_files_only=True)
        if tokenizer.pad_token_id is None:
            tokenizer.pad_token = tokenizer.eos_token
        config = AutoConfig.from_pretrained(a.model_path, local_files_only=True)
        loader = Gemma3ForConditionalGeneration if config.model_type == 'gemma3' else AutoModelForCausalLM
        model = loader.from_pretrained(a.model_path, torch_dtype=torch.bfloat16,
            device_map={'': 'cuda:0'}, local_files_only=True, attn_implementation='sdpa').eval()
        manifest['loader'] = loader.__name__
        manifest['environment'] = dict(python=platform.python_version(), torch=torch.__version__, transformers=transformers.__version__)
        manifest['gpu'] = torch.cuda.get_device_name()
        manifest['model_config_sha256'] = sha(Path(a.model_path)/'config.json')
        manifest['load_seconds'] = time.monotonic()-start
        manifest['generation_config'] = model.generation_config.to_dict()
        save()
        with (a.output/'generations.jsonl').open('w') as handle:
            for i in range(0,len(specs),a.batch_size):
                batch = generate_records(model,tokenizer,specs[i:i+a.batch_size],a.batch_size,a.max_new_tokens)
                for r in batch:
                    handle.write(json.dumps(r,ensure_ascii=False)+'\n')
                handle.flush()
                manifest['completed'] += len(batch)
                save()
                print(f"SAVED {manifest['completed']}/{len(specs)} elapsed={time.monotonic()-start:.1f}s",flush=True)
        manifest.update(status='COMPLETE', finished_utc=datetime.now(timezone.utc).isoformat(),
            elapsed_seconds=time.monotonic()-start, peak_allocated_gb=torch.cuda.max_memory_allocated()/1e9,
            output_sha256=sha(a.output/'generations.jsonl'))
        save()
    except BaseException:
        manifest.update(status='FAILED', error=traceback.format_exc(), elapsed_seconds=time.monotonic()-start)
        save()
        raise


if __name__ == '__main__':
    main()
