from __future__ import annotations

import csv
import io
import re
from collections import Counter
from pathlib import Path

import openpyxl
import requests

SHEET_ID='11EPq1k3dRWyrXfsWJWh405slQ-tyEjJj'
SOURCE_PAGE='https://www.innovacion.mineduc.cl/convocatoria-2025'
SOURCE_SHEET=f'https://docs.google.com/spreadsheets/d/{SHEET_ID}/edit'
OUT=Path('data/education_connectivity_2026/aulas_conectadas_2025_establishments.csv')
SUMMARY=Path('data/education_connectivity_2026/aulas_conectadas_2025_region_summary.csv')
QA=Path('data/education_connectivity_2026/aulas_conectadas_2025_sheet_qa.csv')


def clean(v):
    return re.sub(r'\s+',' ','' if v is None else str(v)).strip()


def norm_rbd(v):
    s=clean(v)
    if not s: return ''
    # Excel may expose integer RBD or a string with check digit.
    if re.fullmatch(r'\d+(?:\.0+)?',s):
        return str(int(float(s)))
    return s.upper()


def download():
    url=f'https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=xlsx'
    r=requests.get(url,timeout=120,allow_redirects=True); r.raise_for_status()
    if not r.content.startswith(b'PK'):
        raise RuntimeError('Public Google Sheet did not return an XLSX workbook')
    return r.content


def main():
    OUT.parent.mkdir(parents=True,exist_ok=True)
    wb=openpyxl.load_workbook(io.BytesIO(download()),read_only=True,data_only=True)
    rows=[]; qa=[]
    for ws in wb.worksheets:
        values=ws.iter_rows(values_only=True)
        header=[clean(v) for v in next(values)]
        idx={name:i for i,name in enumerate(header)}
        required=['RBD','NOMBRE_ESTABLECIMIENTO','REGIÓN','NOMBRE SOSTENEDOR','PROYECTO','ESTADO SELECCIÓN']
        missing=[x for x in required if x not in idx]
        if missing:
            raise RuntimeError(f'{ws.title}: missing columns {missing}')
        status_group='selected' if ws.title.lower().startswith('seleccion') else 'waitlist'
        nonempty=0
        for row_no,row in enumerate(values,start=2):
            rbd=norm_rbd(row[idx['RBD']] if idx['RBD'] < len(row) else '')
            name=clean(row[idx['NOMBRE_ESTABLECIMIENTO']] if idx['NOMBRE_ESTABLECIMIENTO'] < len(row) else '')
            if not rbd and not name:
                continue
            nonempty += 1
            wait_pos=''
            if 'N° Lista Espera' in idx and idx['N° Lista Espera'] < len(row):
                wait_pos=clean(row[idx['N° Lista Espera']])
            rows.append({
                'source_sheet':ws.title,
                'source_row':row_no,
                'selection_group':status_group,
                'rbd':rbd,
                'establishment_name':name,
                'region':clean(row[idx['REGIÓN']]),
                'sponsor_name':clean(row[idx['NOMBRE SOSTENEDOR']]),
                'project':clean(row[idx['PROYECTO']]),
                'selection_status':clean(row[idx['ESTADO SELECCIÓN']]),
                'waitlist_position':wait_pos,
                'source_page':SOURCE_PAGE,
                'source_spreadsheet':SOURCE_SHEET,
            })
        qa.append({'sheet':ws.title,'records':nonempty,'expected_records':700 if status_group=='selected' else 93,'matches_expected':'yes' if nonempty==(700 if status_group=='selected' else 93) else 'no'})

    # Public sheet is keyed by RBD; duplicates across selected/waitlist would be a material QA issue.
    rbd_counts=Counter(r['rbd'] for r in rows if r['rbd'])
    duplicates={k:v for k,v in rbd_counts.items() if v>1}
    qa.append({'sheet':'ALL','records':len(rows),'expected_records':793,'matches_expected':'yes' if len(rows)==793 else 'no'})
    qa.append({'sheet':'UNIQUE_RBD','records':len(rbd_counts),'expected_records':793,'matches_expected':'yes' if not duplicates and len(rbd_counts)==793 else 'no'})

    fields=['source_sheet','source_row','selection_group','rbd','establishment_name','region','sponsor_name','project','selection_status','waitlist_position','source_page','source_spreadsheet']
    with OUT.open('w',encoding='utf-8',newline='') as fh:
        w=csv.DictWriter(fh,fieldnames=fields); w.writeheader(); w.writerows(rows)

    grouped=Counter((r['selection_group'],r['region']) for r in rows)
    summary_rows=[{'selection_group':g,'region':region,'establishments':n} for (g,region),n in sorted(grouped.items())]
    with SUMMARY.open('w',encoding='utf-8',newline='') as fh:
        w=csv.DictWriter(fh,fieldnames=['selection_group','region','establishments']); w.writeheader(); w.writerows(summary_rows)

    with QA.open('w',encoding='utf-8',newline='') as fh:
        w=csv.DictWriter(fh,fieldnames=['sheet','records','expected_records','matches_expected']); w.writeheader(); w.writerows(qa)

    print('records',len(rows),'selected',sum(r['selection_group']=='selected' for r in rows),'waitlist',sum(r['selection_group']=='waitlist' for r in rows),'unique_rbd',len(rbd_counts),'duplicate_rbd',len(duplicates))

if __name__=='__main__':
    main()
