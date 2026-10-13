#!/usr/bin/env python3
"""Test word-sense versus referent/event task construal on frozen AM2iCo pairs."""
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


def build_trials(parent_trials):
    out=[]
    old='Do the expressions marked with <word> and </word> refer to the same entity or concept in their respective contexts? Related entities or concepts can still be different.'
    base='Do the expressions marked with <word> and </word> have the same meaning (sense) in their respective contexts?'
    explicit=' Compare the meanings of the marked expressions, not whether the surrounding events or particular instances are identical. Different instances can share a word sense. For a proper name, compare which named entity it denotes.'
    for r in parent_trials:
        if r['representation']!='full':continue
        assert r['prompt'].count(old)==1
        for criterion,question in [('sense_basic',base),('sense_explicit',base+explicit)]:
            prompt=r['prompt'].replace(old,question).replace('They refer to the same entity or concept.','They have the same meaning (sense).').replace('They refer to different entities or concepts.','They have different meanings (senses).')
            out.append({**r,'representation':criterion,'criterion':criterion,'parent_prompt_sha256':digest(r['prompt']),'prompt':prompt})
    return out


def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--parent',type=Path,required=True)
    ap.add_argument('--output',type=Path,required=True);ap.add_argument('--batch-size',type=int,default=8)
    ap.add_argument('--generation-batch-size',type=int,default=8);args=ap.parse_args()
    parent=json.loads((args.parent/'manifest.json').read_text())
    trials=build_trials([json.loads(x) for x in (args.parent/'trial_specs.jsonl').read_text().splitlines()])
    pairs=set(parent['generation_pairs'])
    gens=[{**r,'generation_task':'joint_relation'} for r in trials if r['pair_id'] in pairs and r['rotation']==0]
    args.output.mkdir(parents=True,exist_ok=False)
    manifest={**{k:parent[k] for k in ['source_revision','source_audit','model_id','model_path','model_revision','tokenizer_revision','chat_template_kwargs','items_sha256','n_items','n_pairs','n_lexeme_families','generation_pairs']},
        'status':'RUNNING','protocol':'am2ico-criterion-followup-v1','started_utc':datetime.now(timezone.utc).isoformat(),
        'parent_run':str(args.parent.resolve()),'parent_specs_sha256':digest((args.parent/'trial_specs.jsonl').read_bytes()),
        'code_sha256':digest(Path(__file__).read_bytes()),'scorer_sha256':digest(Path(score_labels.__code__.co_filename).read_bytes()),
        'batch_size':args.batch_size,'generation_batch_size':args.generation_batch_size,'max_new_tokens':128,
        'n_trials':len(trials),'n_generations':len(gens),'host':platform.node(),'cuda_visible_devices':os.getenv('CUDA_VISIBLE_DEVICES'),
        'seed':20261013,'dtype':'bfloat16','attention':'sdpa',
        'interpretation':'Post-observation task-definition follow-up. All frozen source items, labels, order mappings and generation sample unchanged. Changes question and option descriptions; not an isolated token effect or independent confirmation.'}
    def save(): (args.output/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2))
    save();(args.output/'items.jsonl').write_bytes((args.parent/'items.jsonl').read_bytes())
    for name,rr in [('trial_specs.jsonl',trials),('generation_specs.jsonl',gens)]:
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
    labels=score_labels(model,tokenizer,trials,args.batch_size)
    (args.output/'trials.jsonl').write_text(''.join(json.dumps(r,ensure_ascii=False)+'\n' for r in labels))
    outputs=generate_records(model,tokenizer,gens,args.generation_batch_size,128)
    (args.output/'generations.jsonl').write_text(''.join(json.dumps(r,ensure_ascii=False)+'\n' for r in outputs))
    manifest.update(status='COMPLETE',finished_utc=datetime.now(timezone.utc).isoformat(),elapsed_seconds=time.monotonic()-start,peak_allocated_gb=torch.cuda.max_memory_allocated()/1e9)
    save();print(f'Completed {args.output}',flush=True)


if __name__=='__main__':main()
