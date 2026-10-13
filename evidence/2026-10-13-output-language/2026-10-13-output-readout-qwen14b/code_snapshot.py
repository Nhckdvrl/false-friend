#!/usr/bin/env python3
"""Complete natural responses for existing frozen prompts without altering them."""
import argparse
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import platform
import time
try:
    from scripts.run_doppelganger_diagnostics import generate_records, digest
except ModuleNotFoundError:
    from run_doppelganger_diagnostics import generate_records, digest


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--parent', type=Path, required=True)
    ap.add_argument('--output', type=Path, required=True)
    ap.add_argument('--batch-size', type=int, default=16)
    ap.add_argument('--max-new-tokens', type=int, default=96)
    args = ap.parse_args()
    parent = json.loads((args.parent / 'manifest.json').read_text())
    specs = [json.loads(line) for line in (args.parent / 'trial_specs.jsonl').read_text().splitlines()]
    specs = [{**r, 'generation_task': 'complete_rule_response'} for r in specs
             if r['task'] == 'rule' and r['representation'] != 'masked']
    args.output.mkdir(parents=True, exist_ok=False)
    manifest = {'status': 'RUNNING', 'protocol': 'frozen-prompts-complete-rule-generation-v1',
                'started_utc': datetime.now(timezone.utc).isoformat(), 'host': platform.node(),
                'parent_run': str(args.parent.resolve()), 'parent_manifest_sha256': digest((args.parent/'manifest.json').read_bytes()),
                'parent_specs_sha256': digest((args.parent/'trial_specs.jsonl').read_bytes()),
                'model_id': parent['model_id'], 'model_path': parent['model_path'], 'model_revision': parent['model_revision'],
                'tokenizer_revision': parent['tokenizer_revision'], 'chat_template_kwargs': parent['chat_template_kwargs'],
                'items_sha256': parent['items_sha256'], 'n_generations': len(specs), 'seed': 20261013,
                'batch_size': args.batch_size, 'max_new_tokens': args.max_new_tokens, 'dtype': 'bfloat16',
                'code_sha256': digest(Path(__file__).read_bytes()),
                'scorer_sha256': digest(Path(generate_records.__code__.co_filename).read_bytes()),
                'cuda_visible_devices': os.getenv('CUDA_VISIBLE_DEVICES'),
                'interpretation': 'Post-observation measurement follow-up. All nonmasked rule trials, no error-based item selection. Same prompts. Not independent confirmation.'}
    def save():
        (args.output/'manifest.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2))
    save()
    (args.output/'generation_specs.jsonl').write_text(''.join(json.dumps(r,ensure_ascii=False)+'\n' for r in specs))
    (args.output/'items.jsonl').write_bytes((args.parent/'items.jsonl').read_bytes())
    (args.output/'code_snapshot.py').write_bytes(Path(__file__).read_bytes())
    (args.output/'scorer_snapshot.py').write_bytes(Path(generate_records.__code__.co_filename).read_bytes())
    import torch
    import transformers
    from transformers import AutoModelForCausalLM, AutoTokenizer
    start = time.monotonic()
    torch.set_num_threads(4); torch.manual_seed(20261013)
    tokenizer = AutoTokenizer.from_pretrained(parent['model_path'], local_files_only=True, trust_remote_code=False)
    if tokenizer.pad_token_id is None:
        tokenizer.pad_token = tokenizer.eos_token
    model = AutoModelForCausalLM.from_pretrained(parent['model_path'], torch_dtype=torch.bfloat16,
            local_files_only=True, trust_remote_code=False, device_map={'': 'cuda:0'}, attn_implementation='sdpa').eval()
    manifest['environment'] = {'python': platform.python_version(), 'torch':torch.__version__, 'transformers':transformers.__version__}
    manifest['gpu'] = torch.cuda.get_device_name(); save()
    outputs = generate_records(model, tokenizer, specs, args.batch_size, args.max_new_tokens)
    (args.output/'generations.jsonl').write_text(''.join(json.dumps(r,ensure_ascii=False)+'\n' for r in outputs))
    manifest.update(status='COMPLETE', finished_utc=datetime.now(timezone.utc).isoformat(),
                    elapsed_seconds=time.monotonic()-start, peak_allocated_gb=torch.cuda.max_memory_allocated()/1e9)
    save(); print(f'Completed {args.output}', flush=True)


if __name__ == '__main__':
    main()
