#!/usr/bin/env python3
"""Hold independent model glosses fixed and add original context back."""
import argparse
from datetime import datetime,timezone
import json
import os
from pathlib import Path
import platform
import time
try:
    from scripts.run_doppelganger_diagnostics import score_labels,generate_records,digest
    from scripts.run_am2ico_target_binding import LANGUAGES
except ModuleNotFoundError:
    from run_doppelganger_diagnostics import score_labels,generate_records,digest
    from run_am2ico_target_binding import LANGUAGES


def build_trials(items,outputs,kwargs):
    glosses={}
    for r in outputs:
        if r['generation_task']=='independent_referent':
            lang=r['language'] if r['side']==0 else 'en'
            glosses[(r['contexts'][r['side']],lang)]=r
    pairs={r['pair_id'] for r in outputs if r['generation_task']=='joint_relation'}
    trials=[]
    for item in items:
        if item['pair_id'] not in pairs:continue
        gg=[glosses[(item['contexts'][0],item['language'])],glosses[(item['contexts'][1],'en')]]
        descriptions='\n'.join(f'Independent description {j+1}: {g["generated"]}' for j,g in enumerate(gg))
        raw=f"Text 1 ({LANGUAGES[item['language']]}): {item['contexts'][0]}\nText 2 (English): {item['contexts'][1]}"
        targets=f"Target expression 1 ({LANGUAGES[item['language']]}): {item['targets'][0]}\nTarget expression 2 (English): {item['targets'][1]}"
        for representation,body in [('raw_only',raw),('gloss_only',targets+'\n'+descriptions),('raw_plus_gloss',raw+'\n'+descriptions)]:
            for polarity,order in [('same',[0,1]),('different',[1,0])]:
                predicate='the same meaning (sense)' if polarity=='same' else 'different meanings (senses)'
                question=f'Do the two target expressions have {predicate} in their contexts? Different situations or particular instances can share a word sense. For a proper name, compare which named entity it denotes.'
                trials.append({**item,'representation':representation,'polarity':polarity,'rotation':0 if polarity=='same' else 1,
                    'content_order':order,'label_names':['Yes','No'],'correct_index':0 if item['source_label']=='T' else 1,
                    'original_label_index':0 if item['source_label']=='T' else 1,
                    'glosses':[g['generated'] for g in gg],'gloss_hashes':[digest(g['generated']) for g in gg],
                    'gloss_hit_token_limit':[g['hit_token_limit'] for g in gg],
                    'chat_template_kwargs':kwargs,'prompt':body+'\n'+question+'\nAnswer Yes or No first, then explain briefly in English.'})
    return trials


def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--parent',type=Path,required=True)
    ap.add_argument('--output',type=Path,required=True);ap.add_argument('--batch-size',type=int,default=8)
    ap.add_argument('--generation-batch-size',type=int,default=8);args=ap.parse_args()
    parent=json.loads((args.parent/'manifest.json').read_text())
    items=[json.loads(x) for x in (args.parent/'items.jsonl').read_text().splitlines()]
    outputs=[json.loads(x) for x in (args.parent/'generations.jsonl').read_text().splitlines()]
    trials=build_trials(items,outputs,parent['chat_template_kwargs'])
    genpairs=set()
    for language in LANGUAGES:
        pp={r['pair_id'] for r in trials if r['language']==language}
        genpairs.update(sorted(pp,key=lambda x:digest('gloss-addback-20261013:'+x))[:8])
    gens=[{**r,'generation_task':'joint_relation'} for r in trials if r['pair_id'] in genpairs]
    args.output.mkdir(parents=True,exist_ok=False)
    selected=[r for r in items if r['pair_id'] in {t['pair_id'] for t in trials}]
    manifest={**{k:parent[k] for k in ['source_revision','source_audit','model_id','model_path','model_revision','tokenizer_revision','chat_template_kwargs']},
        'status':'RUNNING','protocol':'am2ico-gloss-addback-v1','started_utc':datetime.now(timezone.utc).isoformat(),
        'parent_run':str(args.parent.resolve()),'parent_generations_sha256':digest((args.parent/'generations.jsonl').read_bytes()),
        'code_sha256':digest(Path(__file__).read_bytes()),'scorer_sha256':digest(Path(score_labels.__code__.co_filename).read_bytes()),
        'batch_size':args.batch_size,'generation_batch_size':args.generation_batch_size,'max_new_tokens':128,
        'n_items':len(selected),'n_pairs':len(selected)//2,'n_lexeme_families':len({r['lexeme_family_id'] for r in selected}),
        'n_trials':len(trials),'n_generations':len(gens),'generation_pairs':sorted(genpairs),
        'host':platform.node(),'cuda_visible_devices':os.getenv('CUDA_VISIBLE_DEVICES'),'seed':20261013,'dtype':'bfloat16','attention':'sdpa',
        'interpretation':'Exploratory context addback holding model-generated gloss strings fixed. Original source-label agreement only. Yes/No and question polarity diagnose readout; polarity is not option rotation. Own glosses differ between models. No independent confirmation or natural computation claim.'}
    def save(): (args.output/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2))
    for name,rr in [('items.jsonl',selected),('trial_specs.jsonl',trials),('generation_specs.jsonl',gens)]:
        (args.output/name).write_text(''.join(json.dumps(r,ensure_ascii=False)+'\n' for r in rr))
    manifest['items_sha256']=digest((args.output/'items.jsonl').read_bytes());save()
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
    generated=generate_records(model,tokenizer,gens,args.generation_batch_size,128)
    (args.output/'generations.jsonl').write_text(''.join(json.dumps(r,ensure_ascii=False)+'\n' for r in generated))
    manifest.update(status='COMPLETE',finished_utc=datetime.now(timezone.utc).isoformat(),elapsed_seconds=time.monotonic()-start,peak_allocated_gb=torch.cuda.max_memory_allocated()/1e9)
    save();print(f'Completed {args.output}',flush=True)


if __name__=='__main__':main()
