#!/usr/bin/env python3
"""Correct target-list asymmetry in the fixed-gloss addback experiment."""
import argparse
from datetime import datetime,timezone
import json
import os
from pathlib import Path
import platform
import time
try:
    from scripts.run_doppelganger_diagnostics import score_labels,generate_records,digest
except ModuleNotFoundError:
    from run_doppelganger_diagnostics import score_labels,generate_records,digest


def build_specs(parent_specs):
    out=[]
    for r in parent_specs:
        if r['representation']!='raw_plus_gloss':continue
        # Preserve the complete target list + descriptions + question used by
        # gloss_only, and prepend the original contexts. A second arm omits
        # only the descriptions while retaining both explicit target strings.
        target_only=next(t for t in parent_specs if t['item_id']==r['item_id'] and t['polarity']==r['polarity'] and t['representation']=='gloss_only')
        boundary='Independent description 1: '
        raw=r['prompt'].split(boundary,1)[0]
        targets=target_only['prompt'].split(boundary,1)[0]
        assert target_only['prompt'].count(boundary)==1
        question=r['prompt'].rsplit('\nDo the two target expressions have ',1)[1]
        for name,prompt in [('raw_targets_gloss',raw+target_only['prompt']),
                            ('raw_targets',raw+targets+'Do the two target expressions have '+question)]:
            out.append({**r,'representation':name,'parent_prompt_sha256':digest(r['prompt']),
                        'matched_gloss_prompt_sha256':digest(target_only['prompt']),'prompt':prompt})
    return out


def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--parent',type=Path,required=True)
    ap.add_argument('--output',type=Path,required=True);ap.add_argument('--batch-size',type=int,default=8)
    ap.add_argument('--generation-batch-size',type=int,default=8);args=ap.parse_args()
    parent=json.loads((args.parent/'manifest.json').read_text())
    gens=build_specs([json.loads(x) for x in (args.parent/'generation_specs.jsonl').read_text().splitlines()])
    args.output.mkdir(parents=True,exist_ok=False)
    manifest={**{k:parent[k] for k in ['source_revision','source_audit','model_id','model_path','model_revision','tokenizer_revision','chat_template_kwargs','items_sha256','n_items','n_pairs','n_lexeme_families','generation_pairs']},
        'status':'RUNNING','protocol':'am2ico-target-restatement-v1','started_utc':datetime.now(timezone.utc).isoformat(),
        'parent_run':str(args.parent.resolve()),'parent_specs_sha256':digest((args.parent/'generation_specs.jsonl').read_bytes()),
        'code_sha256':digest(Path(__file__).read_bytes()),'scorer_sha256':digest(Path(score_labels.__code__.co_filename).read_bytes()),
        'batch_size':args.batch_size,'generation_batch_size':args.generation_batch_size,'max_new_tokens':128,
        'n_trials':0,'n_generations':len(gens),'host':platform.node(),'cuda_visible_devices':os.getenv('CUDA_VISIBLE_DEVICES'),
        'seed':20261013,'dtype':'bfloat16','attention':'sdpa',
        'interpretation':'Post-observation correction of target-list asymmetry. Same frozen 24-pair natural-generation sample and both polarities. Matched context addback preserves target list and gloss text exactly; additional raw+targets arm tests target restatement without glosses. Not independent confirmation.'}
    def save(): (args.output/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2))
    save();(args.output/'items.jsonl').write_bytes((args.parent/'items.jsonl').read_bytes())
    for name,rr in [('generation_specs.jsonl',gens)]:
        (args.output/name).write_text(''.join(json.dumps(r,ensure_ascii=False)+'\n' for r in rr))
    (args.output/'code_snapshot.py').write_bytes(Path(__file__).read_bytes())
    (args.output/'scorer_snapshot.py').write_bytes(Path(score_labels.__code__.co_filename).read_bytes())
    import torch
    import transformers
    from transformers import AutoModelForCausalLM,AutoTokenizer
    start=time.monotonic();torch.set_num_threads(4);torch.manual_seed(20261013)
    tokenizer=AutoTokenizer.from_pretrained(parent['model_path'],local_files_only=True,trust_remote_code=False)
    if tokenizer.pad_token_id is None:tokenizer.pad_token=tokenizer.eos_token
    model=AutoModelForCausalLM.from_pretrained(parent['model_path'],local_files_only=True,trust_remote_code=False,
                torch_dtype=torch.bfloat16,device_map={'':'cuda:0'},attn_implementation='sdpa').eval()
    manifest['environment']={'python':platform.python_version(),'torch':torch.__version__,'transformers':transformers.__version__}
    manifest['gpu']=torch.cuda.get_device_name();manifest['chat_template_sha256']=digest(tokenizer.chat_template or '');save()
    outputs=generate_records(model,tokenizer,gens,args.generation_batch_size,128)
    (args.output/'generations.jsonl').write_text(''.join(json.dumps(r,ensure_ascii=False)+'\n' for r in outputs))
    manifest.update(status='COMPLETE',finished_utc=datetime.now(timezone.utc).isoformat(),elapsed_seconds=time.monotonic()-start,peak_allocated_gb=torch.cuda.max_memory_allocated()/1e9)
    save();print(f'Completed {args.output}',flush=True)


if __name__=='__main__':main()
