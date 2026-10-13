#!/usr/bin/env python3
"""Archive completed AM2iCo diagnostic runs with corpus attribution and hashes."""
import argparse
import hashlib
import json
from pathlib import Path
import shutil


def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--destination',type=Path,required=True)
    ap.add_argument('--source',type=Path,default=Path('data/raw/AM2iCo'));ap.add_argument('runs',type=Path,nargs='+')
    args=ap.parse_args();args.destination.mkdir(parents=True,exist_ok=True)
    shutil.copyfile(args.source/'LICENSE.md',args.destination/'SOURCE_LICENSE.md')
    shutil.copyfile(args.source/'README.md',args.destination/'SOURCE_README.md')
    for run in args.runs:
        m=json.loads((run/'manifest.json').read_text())
        if m['status']!='COMPLETE' or not m['protocol'].startswith('am2ico-'):raise ValueError(f'Unfinished/unscoped {run}')
        out=args.destination/run.name;out.mkdir(exist_ok=False);files={}
        for f in sorted(run.iterdir()):
            if f.is_file() and f.suffix in {'.json','.jsonl','.py'}:
                shutil.copyfile(f,out/f.name);files[f.name]={'sha256':hashlib.sha256(f.read_bytes()).hexdigest(),'bytes':f.stat().st_size}
        (out/'raw_provenance.json').write_text(json.dumps({'local_raw_run':str(run.resolve()),'files':files,
            'source':'https://github.com/cambridgeltl/AM2iCo','source_revision':m['source_revision'],
            'attribution':'Qianchu Liu, Edoardo M. Ponti, Diana McCarthy, Ivan Vulić, Anna Korhonen. AM2iCo, EMNLP 2021.',
            'policy':'Full selected source records and original labels retained with attribution. New sampling/prompts/model output/reviews identified in manifests. Source-repository CC BY 4.0 license copied at bundle root. Agent review is not independent human gold.'},ensure_ascii=False,indent=2))
        print(out)


if __name__=='__main__':main()
