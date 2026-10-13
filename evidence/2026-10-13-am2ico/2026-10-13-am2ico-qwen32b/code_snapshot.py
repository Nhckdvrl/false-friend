#!/usr/bin/env python3
"""Published AM2iCo target-change pairs: relation decisions and independent glosses."""
import argparse
from collections import defaultdict
import csv
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import platform
import re
import subprocess
import time
import unicodedata
try:
    from scripts.run_doppelganger_diagnostics import score_labels, generate_records, digest
except ModuleNotFoundError:
    from run_doppelganger_diagnostics import score_labels, generate_records, digest

SOURCE_SHA = '2003865050bc9a9e84f2bcb4979f03734bddab28'
LANGUAGES = {'de':'German','zh':'Chinese','ja':'Japanese'}


def target(text):
    found=re.findall(r'<word>(.*?)</word>',text)
    if len(found)!=1: raise ValueError('Expected one marked target')
    return found[0]


def bare(text):
    return re.sub(r'\s+',' ',re.sub(r'</?word>','',text)).strip()


def select_items(source, count=64):
    items=[]; audit={}
    for language in LANGUAGES:
        path=source/'data'/language/'train.tsv'
        # The released TSV contains literal quotation marks, not CSV quoting.
        # Default csv quoting can merge lines and corrupt target/source indices.
        rows=list(csv.DictReader(path.open(),delimiter='\t',quoting=csv.QUOTE_NONE))
        file_sha=digest(path.read_bytes())
        groups=defaultdict(list)
        for i,r in enumerate(rows):
            if r['label'] not in {'T','F'}:raise ValueError(r['label'])
            try: words=[target(r['context1']),target(r['context2'])]
            except ValueError: continue
            contexts=[r['context1'],r['context2']]
            groups[tuple(bare(c) for c in contexts)].append({'source_line':i+2,'source_label':r['label'],
                'contexts':contexts,'targets':words})
        candidates=[]
        for common,rr in groups.items():
            positives=[r for r in rr if r['source_label']=='T']; negatives=[r for r in rr if r['source_label']=='F']
            for pos in positives:
                for neg in negatives:
                    changed=[i for i in range(2) if pos['targets'][i]!=neg['targets'][i]]
                    if len(changed)!=1:continue
                    pairid=digest(json.dumps([language,common,pos['targets'],neg['targets']],ensure_ascii=False))
                    family=unicodedata.normalize('NFC',pos['targets'][1]).strip().casefold()
                    candidates.append((pairid,family,pos,neg,changed[0]))
        seen=set(); chosen=[]
        for pairid,family,pos,neg,changed in sorted(candidates,key=lambda r:digest('am2ico-target-20261013:'+r[0])):
            if family in seen:continue
            seen.add(family);chosen.append((pairid,family,pos,neg,changed))
            if len(chosen)==count:break
        if len(chosen)!=count:raise ValueError('Insufficient distinct positive target families')
        for pairid,family,pos,neg,changed in chosen:
            for r in [pos,neg]:
                items.append({**r,'item_id':f'{language}:{pairid}:{r["source_label"]}',
                              'pair_id':f'{language}:{pairid}', 'lexeme_family_id':f'en:{family}',
                              'language':language,'changed_side':changed,'source_split':'train',
                              'source_file':f'data/{language}/train.tsv','source_revision':SOURCE_SHA,
                              'source_file_sha256':file_sha,
                              'label_review':'published_original_label_not_individually_human_validated_here'})
        audit[language]={'source_rows':len(rows),'candidate_pairs':len(candidates),'selected_pairs':len(chosen),
                         'positive_target_types':len(seen),'file_sha256':file_sha}
    return items,audit


def build_trials(items, template_kwargs):
    trials=[]
    for item in items:
        for representation in ['full','target_only']:
            if representation=='full':
                content=f"Text 1 ({LANGUAGES[item['language']]}): {item['contexts'][0]}\nText 2 (English): {item['contexts'][1]}"
                question='Do the expressions marked with <word> and </word> refer to the same entity or concept in their respective contexts? Related entities or concepts can still be different.'
            else:
                content=f"Expression 1 ({LANGUAGES[item['language']]}): {item['targets'][0]}\nExpression 2 (English): {item['targets'][1]}"
                question='Do these expressions refer to the same entity or concept? Related entities or concepts can still be different.'
            for rotation,order in enumerate(([0,1],[1,0])):
                options=['They refer to the same entity or concept.','They refer to different entities or concepts.']
                prompt=content+'\n'+question+'\n'+'\n'.join(f'{letter}) {options[idx]}' for letter,idx in zip('AB',order))
                prompt+='\nStart with the correct option letter (A or B), then briefly explain the two referents in English.'
                gold=0 if item['source_label']=='T' else 1
                trials.append({**item,'representation':representation,'rotation':rotation,'content_order':order,
                               'label_names':'AB','correct_index':gold if representation=='full' else None,
                               'original_label_index':gold,'prompt':prompt,'chat_template_kwargs':template_kwargs})
    return trials


def generation_specs(items,trials):
    pairs=[]
    for language in LANGUAGES:
        available={r['pair_id'] for r in items if r['language']==language}
        pairs+=sorted(available,key=lambda x:digest('am2ico-generations-20261013:'+x))[:16]
    selected=set(pairs)
    specs=[{**r,'generation_task':'joint_relation'} for r in trials if r['pair_id'] in selected and r['representation']=='full' and r['rotation']==0]
    seen=set()
    for item in items:
        if item['pair_id'] not in selected:continue
        for side in [0,1]:
            context=item['contexts'][side];lang=LANGUAGES[item['language']] if side==0 else 'English'
            ident=(context,lang)
            if ident in seen:continue
            seen.add(ident)
            specs.append({**item,'generation_task':'independent_referent','side':side,'target':item['targets'][side],
                          'prompt':f'The following text is in {lang}. What entity or concept does the expression marked with <word> and </word> refer to here? Give its identity or a short definition in English, rather than its grammatical role.\n{context}',
                          'chat_template_kwargs':trials[0]['chat_template_kwargs']})
    return specs,pairs


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--source',type=Path,default=Path('data/raw/AM2iCo'))
    ap.add_argument('--model-path',type=Path,required=True);ap.add_argument('--model-id',required=True)
    ap.add_argument('--output',type=Path,required=True);ap.add_argument('--batch-size',type=int,default=8)
    ap.add_argument('--generation-batch-size',type=int,default=8);ap.add_argument('--disable-thinking',action='store_true')
    ap.add_argument('--dry-run',action='store_true');args=ap.parse_args()
    revision=subprocess.check_output(['git','-C',str(args.source),'rev-parse','HEAD'],text=True).strip()
    if revision!=SOURCE_SHA:raise ValueError('Unreviewed revision')
    items,audit=select_items(args.source);kwargs={'enable_thinking':False} if args.disable_thinking else {}
    trials=build_trials(items,kwargs);generations,pairs=generation_specs(items,trials)
    args.output.mkdir(parents=True,exist_ok=False)
    manifest={'status':'PREPARED' if args.dry_run else 'RUNNING','protocol':'am2ico-target-binding-v1',
              'started_utc':datetime.now(timezone.utc).isoformat(),'source_revision':revision,'source_audit':audit,
              'model_id':args.model_id,'model_path':str(args.model_path),'model_revision':args.model_path.name,
              'tokenizer_revision':args.model_path.name,'chat_template_kwargs':kwargs,'seed':20261013,
              'n_items':len(items),'n_pairs':len(items)//2,'n_lexeme_families':len({r['lexeme_family_id'] for r in items}),
              'n_trials':len(trials),'n_generations':len(generations),'generation_pairs':pairs,
              'batch_size':args.batch_size,'generation_batch_size':args.generation_batch_size,'max_new_tokens':128,
              'host':platform.node(),'cuda_visible_devices':os.getenv('CUDA_VISIBLE_DEVICES'),'dtype':'bfloat16','attention':'sdpa',
              'code_sha256':digest(Path(__file__).read_bytes()),'scorer_sha256':digest(Path(score_labels.__code__.co_filename).read_bytes()),
              'interpretation':'Published task adaptation on a pre-output selected training-source subset, not reproduction of encoder results. Word-only agreement is original-label recoverability. Source labels may have referent/granularity errors; no semantic gold extrapolation.'}
    def save(): (args.output/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2))
    for name,rr in [('items.jsonl',items),('trial_specs.jsonl',trials),('generation_specs.jsonl',generations)]:
        (args.output/name).write_text(''.join(json.dumps(r,ensure_ascii=False)+'\n' for r in rr))
    manifest['items_sha256']=digest((args.output/'items.jsonl').read_bytes());save()
    (args.output/'code_snapshot.py').write_bytes(Path(__file__).read_bytes())
    (args.output/'scorer_snapshot.py').write_bytes(Path(score_labels.__code__.co_filename).read_bytes())
    if args.dry_run: print(json.dumps(manifest,ensure_ascii=False,indent=2));return
    import torch
    import transformers
    from transformers import AutoModelForCausalLM,AutoTokenizer
    start=time.monotonic();torch.set_num_threads(4);torch.manual_seed(20261013)
    tokenizer=AutoTokenizer.from_pretrained(args.model_path,local_files_only=True,trust_remote_code=False)
    if tokenizer.pad_token_id is None:tokenizer.pad_token=tokenizer.eos_token
    model=AutoModelForCausalLM.from_pretrained(args.model_path,local_files_only=True,trust_remote_code=False,
                torch_dtype=torch.bfloat16,device_map={'':'cuda:0'},attn_implementation='sdpa').eval()
    manifest['environment']={'python':platform.python_version(),'torch':torch.__version__,'transformers':transformers.__version__}
    manifest['gpu']=torch.cuda.get_device_name();manifest['chat_template_sha256']=digest(tokenizer.chat_template or '');save()
    labels=score_labels(model,tokenizer,trials,args.batch_size)
    (args.output/'trials.jsonl').write_text(''.join(json.dumps(r,ensure_ascii=False)+'\n' for r in labels))
    outputs=generate_records(model,tokenizer,generations,args.generation_batch_size,128)
    (args.output/'generations.jsonl').write_text(''.join(json.dumps(r,ensure_ascii=False)+'\n' for r in outputs))
    manifest.update(status='COMPLETE',finished_utc=datetime.now(timezone.utc).isoformat(),elapsed_seconds=time.monotonic()-start,
                    peak_allocated_gb=torch.cuda.max_memory_allocated()/1e9)
    save();print(f'Completed {args.output}',flush=True)


if __name__=='__main__':main()
