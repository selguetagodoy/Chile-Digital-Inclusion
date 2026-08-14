from __future__ import annotations

import csv
import io
from pathlib import Path
import openpyxl
import requests

URL='https://www.subtel.gob.cl/wp-content/uploads/2026/05/1_SERIES_CONEXIONES_INTERNET_FIJA_MAR26_040526.xlsx'
OUT=Path('data/subtel_sector_series/latest_fixed_technology_audit.csv')


def val(v):
    if v is None: return ''
    return str(v).strip()


def main():
    r=requests.get(URL,timeout=180); r.raise_for_status()
    wb=openpyxl.load_workbook(io.BytesIO(r.content),read_only=True,data_only=True)
    ws=wb['7.7.CO_TEC_FIJAS']
    rows=[]
    # Preserve the first 10 columns and both header/data context.
    for row_no,row in enumerate(ws.iter_rows(min_row=1,max_row=ws.max_row,max_col=10,values_only=True),start=1):
        vals=list(row)
        if row_no<=8 or any('2026' in val(v) for v in vals[:3]):
            rows.append({'source_row':row_no,**{f'col{i+1}':val(vals[i]) for i in range(10)}})
    # Also append the final five non-empty rows.
    tail=[]
    for row_no,row in enumerate(ws.iter_rows(min_row=max(1,ws.max_row-12),max_row=ws.max_row,max_col=10,values_only=True),start=max(1,ws.max_row-12)):
        vals=list(row)
        if any(val(v) for v in vals):
            tail.append({'source_row':row_no,**{f'col{i+1}':val(vals[i]) for i in range(10)}})
    seen={r['source_row'] for r in rows}
    rows.extend(r for r in tail if r['source_row'] not in seen)
    OUT.parent.mkdir(parents=True,exist_ok=True)
    fields=['source_row']+[f'col{i}' for i in range(1,11)]
    with OUT.open('w',encoding='utf-8',newline='') as fh:
        w=csv.DictWriter(fh,fieldnames=fields); w.writeheader(); w.writerows(rows)
    print(rows)

if __name__=='__main__': main()
