#!/usr/bin/env python3
"""Archive a completed locally authored experiment, including its full prompts."""
import argparse
import hashlib
import json
from pathlib import Path
import shutil


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--destination',type=Path,required=True);ap.add_argument('runs',type=Path,nargs='+')
    args=ap.parse_args()
    for run in args.runs:
        manifest=json.loads((run/'manifest.json').read_text())
        if manifest['status']!='COMPLETE':raise ValueError(f'Incomplete: {run}')
        # This exporter is intentionally scoped to our original authored corpus.
        if manifest['protocol'] not in {'output-language-cycle-v1','frozen-prompts-complete-rule-generation-v1'}:
            raise ValueError('Protocol may contain third-party raw corpus; use scoped packaging')
        out=args.destination/run.name;out.mkdir(parents=True,exist_ok=False);files={}
        for f in sorted(run.iterdir()):
            if f.is_file() and f.suffix in {'.json','.jsonl','.py'}:
                shutil.copyfile(f,out/f.name)
                files[f.name]={'sha256':hashlib.sha256(f.read_bytes()).hexdigest(),'bytes':f.stat().st_size}
        (out/'raw_provenance.json').write_text(json.dumps({'local_raw_run':str(run.resolve()),'files':files,
            'policy':'Full locally authored stimuli and prompts preserved. Agent review is nonblind and is not independent human gold.'},ensure_ascii=False,indent=2))
        print(out)


if __name__=='__main__':main()
