from __future__ import annotations

import csv
import re
import tempfile
from pathlib import Path

import pdfplumber
import requests

FILE_ID = '10u8dJY48ZopFNwzwnzDGUTfYo9xU9_W5'
SOURCE_PAGE = 'https://www.innovacion.mineduc.cl/iniciativas/transformaci%C3%B3n-digital/infraestructura-digital-educativa/aulas-conectadas-convocatoria-2025'
SOURCE_DRIVE = f'https://drive.google.com/file/d/{FILE_ID}/view'
OUT = Path('data/education_connectivity_2026/aulas_conectadas_2025_rex775_rbd_candidates.csv')
SUMMARY = Path('data/education_connectivity_2026/aulas_conectadas_2025_rex775_extraction_summary.csv')


def download_pdf() -> bytes:
    urls = [
        f'https://drive.usercontent.google.com/download?id={FILE_ID}&export=download&confirm=t',
        f'https://drive.google.com/uc?export=download&id={FILE_ID}',
    ]
    errors=[]
    for url in urls:
        try:
            r=requests.get(url,timeout=120,allow_redirects=True); r.raise_for_status()
            if r.content[:4] == b'%PDF' or 'application/pdf' in r.headers.get('content-type',''):
                return r.content
            errors.append(f'unexpected content type {r.headers.get("content-type")}')
        except Exception as exc:
            errors.append(f'{type(exc).__name__}: {exc}')
    raise RuntimeError(' | '.join(errors))


def clean(v):
    return re.sub(r'\s+',' ','' if v is None else str(v)).strip()


def rbd_candidates(text: str):
    out=[]
    for base,dv in re.findall(r'(?<!\d)(\d{2,5})(?:-([0-9Kk]))?(?!\d)',text):
        n=int(base)
        if 100 <= n <= 20000 and n not in {775,450,8040,2025,2026}:
            out.append(f'{n}-{dv.upper()}' if dv else str(n))
    return out


def main():
    OUT.parent.mkdir(parents=True,exist_ok=True)
    body=download_pdf(); rows=[]
    pages_with_text=0; text_chars=0; pages_with_tables=0; tables_seen=0; rbd_tables=0
    with tempfile.NamedTemporaryFile(suffix='.pdf') as tmp:
        tmp.write(body); tmp.flush()
        with pdfplumber.open(tmp.name) as pdf:
            pages=len(pdf.pages)
            for pageno,page in enumerate(pdf.pages,start=1):
                text=page.extract_text() or ''
                if text.strip():
                    pages_with_text += 1; text_chars += len(text)
                tables=page.extract_tables() or []
                if tables: pages_with_tables += 1
                for table_no,table in enumerate(tables,start=1):
                    tables_seen += 1
                    normalized=[[clean(c) for c in row] for row in table if row]
                    header=' | '.join(' '.join(r) for r in normalized[:4]).upper()
                    if 'RBD' not in header:
                        continue
                    rbd_tables += 1
                    for row_no,cells in enumerate(normalized,start=1):
                        raw=' | '.join(cells)
                        for rbd in rbd_candidates(raw):
                            rows.append({'page':pageno,'table':table_no,'row':row_no,'rbd_candidate':rbd,'raw_cells':raw,'source_page':SOURCE_PAGE,'source_document':SOURCE_DRIVE})

                # Text fallback only where RBD is written on the same line.
                for line_no,line in enumerate(text.splitlines(),start=1):
                    if 'RBD' not in line.upper():
                        continue
                    raw=clean(line)
                    for rbd in rbd_candidates(raw):
                        rows.append({'page':pageno,'table':'','row':line_no,'rbd_candidate':rbd,'raw_cells':raw,'source_page':SOURCE_PAGE,'source_document':SOURCE_DRIVE})

    dedup=[]; seen=set()
    for r in rows:
        key=(r['rbd_candidate'],r['raw_cells'])
        if key not in seen:
            seen.add(key); dedup.append(r)

    fields=['page','table','row','rbd_candidate','raw_cells','source_page','source_document']
    with OUT.open('w',encoding='utf-8',newline='') as fh:
        w=csv.DictWriter(fh,fieldnames=fields); w.writeheader(); w.writerows(dedup)
    with SUMMARY.open('w',encoding='utf-8',newline='') as fh:
        w=csv.DictWriter(fh,fieldnames=['metric','value','note']); w.writeheader(); w.writerows([
            {'metric':'pdf_bytes','value':len(body),'note':'Downloaded public REX 775'},
            {'metric':'pages','value':pages,'note':'PDF pages'},
            {'metric':'pages_with_text','value':pages_with_text,'note':'Pages with extractable text; no OCR used'},
            {'metric':'text_characters','value':text_chars,'note':'Extractable text characters'},
            {'metric':'pages_with_tables','value':pages_with_tables,'note':'Pages with detected tables'},
            {'metric':'tables','value':tables_seen,'note':'Detected tables'},
            {'metric':'tables_with_rbd_header','value':rbd_tables,'note':'Tables whose first rows explicitly mention RBD'},
            {'metric':'rbd_candidate_rows','value':len(dedup),'note':'Audit candidates, not confirmed establishments until crosswalk to official directory'},
            {'metric':'unique_rbd_candidates','value':len({r["rbd_candidate"] for r in dedup}),'note':'Unique candidate values'},
        ])
    print('pages',pages,'tables',tables_seen,'rbd_tables',rbd_tables,'candidates',len(dedup))

if __name__=='__main__':
    main()
