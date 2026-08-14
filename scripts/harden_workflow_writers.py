#!/usr/bin/env python3
"""Harden every GitHub Actions workflow that writes back to main.

All writer workflows share one concurrency group, preventing independent jobs
from racing on refs/heads/main. Workflows that lacked a pull --rebase before
push also receive one. The transformation is idempotent.
"""
from __future__ import annotations

from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
WF_DIR=ROOT/'.github'/'workflows'
BLOCK=['concurrency:','  group: main-writers','  cancel-in-progress: false','']


def with_shared_concurrency(lines:list[str])->list[str]:
    # Remove an existing top-level concurrency block, if present.
    start=None
    for i,line in enumerate(lines):
        if line.strip()=='concurrency:' and not line.startswith((' ','\t')):
            start=i; break
    if start is not None:
        end=start+1
        while end<len(lines):
            line=lines[end]
            if line and not line.startswith((' ','\t')):
                break
            end+=1
        lines=lines[:start]+lines[end:]

    jobs=None
    for i,line in enumerate(lines):
        if line.strip()=='jobs:' and not line.startswith((' ','\t')):
            jobs=i; break
    if jobs is None:
        raise RuntimeError('Workflow has no top-level jobs block')
    return lines[:jobs]+BLOCK+lines[jobs:]


def ensure_rebase(lines:list[str])->list[str]:
    text='\n'.join(lines)
    if 'git push' not in text or 'git pull --rebase origin main' in text:
        return lines
    out=[]
    inserted=0
    for line in lines:
        stripped=line.strip()
        if 'git push' in stripped and not stripped.startswith('#'):
            indent=line[:len(line)-len(line.lstrip())]
            out.append(indent+'git pull --rebase origin main')
            inserted+=1
        out.append(line)
    if inserted==0:
        raise RuntimeError('git push detected but no push line could be hardened')
    return out


def main():
    changed=[]
    writers=0
    for path in sorted(WF_DIR.glob('*.y*ml')):
        original=path.read_text(encoding='utf-8')
        if 'git push' not in original:
            continue
        writers+=1
        lines=original.splitlines()
        lines=with_shared_concurrency(lines)
        lines=ensure_rebase(lines)
        updated='\n'.join(lines).rstrip()+'\n'
        if updated!=original:
            path.write_text(updated,encoding='utf-8')
            changed.append(str(path.relative_to(ROOT)))
    print(f'writer_workflows={writers}')
    print(f'changed_workflows={len(changed)}')
    for path in changed:
        print(path)


if __name__=='__main__':
    main()
