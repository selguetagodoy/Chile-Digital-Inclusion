from __future__ import annotations

import csv
import re
import tempfile
from pathlib import Path

import pdfplumber
import requests

FILE_ID = '1f7X3wOOmUOjM_Jf7fSYNox3fGuJVG88v'
SOURCE_PAGE = 'https://www.innovacion.mineduc.cl/iniciativas/cpe2030-2025'
SOURCE_DRIVE = f'https://drive.google.com/file/d/{FILE_ID}/view?usp=sharing'
OUT = Path('data/education_connectivity_2026/cpe2030_2026_rex497_rbd_candidates.csv')
SUMMARY = Path('data/education_connectivity_2026/cpe2030_2026_rex497_extraction_summary.csv')
TEXT_AUDIT = Path('data/education_connectivity_2026/cpe2030_2026_rex497_text_audit.csv')


def download_pdf() -> bytes:
    urls = [
        f'https://drive.usercontent.google.com/download?id={FILE_ID}&export=download&confirm=t',
        f'https://drive.google.com/uc?export=download&id={FILE_ID}',
    ]
    errors = []
    for url in urls:
        try:
            r = requests.get(url, timeout=90, allow_redirects=True)
            r.raise_for_status()
            body = r.content
            if body[:4] == b'%PDF' or 'application/pdf' in r.headers.get('content-type', ''):
                return body
            errors.append(f'{url}: unexpected content-type {r.headers.get("content-type")} bytes={len(body)}')
        except Exception as exc:
            errors.append(f'{url}: {type(exc).__name__}: {exc}')
    raise RuntimeError('Could not download public PDF: ' + ' | '.join(errors))


def clean(value) -> str:
    if value is None:
        return ''
    return re.sub(r'\s+', ' ', str(value)).strip()


def candidates_from_text(text: str) -> list[str]:
    found = []
    for token in re.findall(r'(?<!\d)(\d{1,5})(?:-([0-9Kk]))?(?!\d)', text):
        base, dv = token
        num = int(base)
        if 100 <= num <= 20000 and num not in {497, 2025, 2026, 2030}:
            found.append(f'{num}-{dv.upper()}' if dv else str(num))
    return found


def main() -> None:
    OUT.parent.mkdir(parents=True, exist_ok=True)
    pdf_bytes = download_pdf()
    rows = []
    text_rows = []
    pages_with_tables = 0
    tables_seen = 0
    pages_with_text = 0
    total_text_chars = 0
    lines_mentioning_rbd = 0

    with tempfile.NamedTemporaryFile(suffix='.pdf') as tmp:
        tmp.write(pdf_bytes); tmp.flush()
        with pdfplumber.open(tmp.name) as pdf:
            page_count = len(pdf.pages)
            for pageno, page in enumerate(pdf.pages, start=1):
                text = page.extract_text() or ''
                if text.strip():
                    pages_with_text += 1
                    total_text_chars += len(text)
                    for line_no, line in enumerate(text.splitlines(), start=1):
                        if 'RBD' not in line.upper():
                            continue
                        lines_mentioning_rbd += 1
                        cleaned = clean(line)
                        cands = candidates_from_text(cleaned)
                        text_rows.append({
                            'page': pageno,
                            'line': line_no,
                            'mentions_rbd': 'yes',
                            'numeric_candidates': '|'.join(cands),
                            'text': cleaned,
                            'source_document': SOURCE_DRIVE,
                        })
                        for rbd in cands:
                            rows.append({
                                'page': pageno,
                                'table': '',
                                'row': line_no,
                                'rbd_candidate': rbd,
                                'table_header_mentions_rbd': 'text_line_mentions_rbd',
                                'raw_cells': cleaned,
                                'source_page': SOURCE_PAGE,
                                'source_document': SOURCE_DRIVE,
                            })

                tables = page.extract_tables() or []
                if tables:
                    pages_with_tables += 1
                for table_no, table in enumerate(tables, start=1):
                    tables_seen += 1
                    normalized = [[clean(c) for c in row] for row in table if row]
                    header_text = ' | '.join(' '.join(r) for r in normalized[:3]).upper()
                    has_rbd_header = 'RBD' in header_text
                    for row_no, cells in enumerate(normalized, start=1):
                        joined = ' | '.join(cells)
                        if not joined:
                            continue
                        for rbd in candidates_from_text(joined):
                            if not has_rbd_header:
                                continue
                            rows.append({
                                'page': pageno,
                                'table': table_no,
                                'row': row_no,
                                'rbd_candidate': rbd,
                                'table_header_mentions_rbd': 'yes',
                                'raw_cells': joined,
                                'source_page': SOURCE_PAGE,
                                'source_document': SOURCE_DRIVE,
                            })

    dedup = []
    seen = set()
    for row in rows:
        key = (row['rbd_candidate'], row['raw_cells'])
        if key not in seen:
            seen.add(key); dedup.append(row)

    fields = ['page','table','row','rbd_candidate','table_header_mentions_rbd','raw_cells','source_page','source_document']
    with OUT.open('w', encoding='utf-8', newline='') as fh:
        w = csv.DictWriter(fh, fieldnames=fields); w.writeheader(); w.writerows(dedup)

    text_fields = ['page','line','mentions_rbd','numeric_candidates','text','source_document']
    with TEXT_AUDIT.open('w', encoding='utf-8', newline='') as fh:
        w = csv.DictWriter(fh, fieldnames=text_fields); w.writeheader(); w.writerows(text_rows)

    table_rbd_rows = sum(r['table_header_mentions_rbd'] == 'yes' for r in dedup)
    with SUMMARY.open('w', encoding='utf-8', newline='') as fh:
        w = csv.DictWriter(fh, fieldnames=['metric','value','note']); w.writeheader()
        w.writerows([
            {'metric':'pdf_bytes','value':len(pdf_bytes),'note':'Downloaded public REX 497 document'},
            {'metric':'pages','value':page_count,'note':'PDF pages'},
            {'metric':'pages_with_text','value':pages_with_text,'note':'Pages with extractable text layer; no OCR used'},
            {'metric':'text_characters','value':total_text_chars,'note':'Extractable text characters across document'},
            {'metric':'lines_mentioning_rbd','value':lines_mentioning_rbd,'note':'Text lines explicitly containing RBD'},
            {'metric':'pages_with_tables','value':pages_with_tables,'note':'Pages where pdfplumber detected at least one table'},
            {'metric':'tables','value':tables_seen,'note':'Detected tables'},
            {'metric':'rbd_candidates_all','value':len(dedup),'note':'Candidates only from RBD-labelled table contexts or text lines explicitly mentioning RBD; audit before treating as establishments'},
            {'metric':'rbd_candidates_in_rbd_header_tables','value':table_rbd_rows,'note':'Candidates from tables whose first rows explicitly mention RBD'},
        ])

    print(f'pages={page_count} text_pages={pages_with_text} text_chars={total_text_chars} rbd_lines={lines_mentioning_rbd} tables={tables_seen} candidates={len(dedup)}')


if __name__ == '__main__':
    main()
