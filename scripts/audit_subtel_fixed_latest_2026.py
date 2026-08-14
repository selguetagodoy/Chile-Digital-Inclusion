from __future__ import annotations

import csv
import io
import re
from collections import defaultdict
from pathlib import Path
import openpyxl
import requests

URL='https://www.subtel.gob.cl/wp-content/uploads/2026/05/1_SERIES_CONEXIONES_INTERNET_FIJA_MAR26_040526.xlsx'
OUT=Path('data/subtel_sector_series/latest_fixed_technology_audit.csv')
REGIONAL_OUT=Path('data/subtel_sector_series/latest_fixed_technology_regional_audit.csv')


def val(v):
    if v is None: return ''
    return re.sub(r'\s+',' ',str(v)).strip()


def number(v):
    try: return float(v)
    except (TypeError,ValueError): return None


def normalize(s):
    return val(s).lower().replace('ó','o').replace('í','i').replace('á','a').replace('é','e').replace('ú','u')


def main():
    r=requests.get(URL,timeout=180); r.raise_for_status()
    wb=openpyxl.load_workbook(io.BytesIO(r.content),read_only=True,data_only=True)

    ws=wb['7.7.CO_TEC_FIJAS']
    rows=[]
    for row_no,row in enumerate(ws.iter_rows(min_row=1,max_row=ws.max_row,max_col=10,values_only=True),start=1):
        vals=list(row)
        if row_no<=8 or any('2026' in val(v) for v in vals[:3]):
            rows.append({'source_row':row_no,**{f'col{i+1}':val(vals[i]) for i in range(10)}})
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

    # The historical national technology sheet has stale headers in recent
    # rows. Audit the row-oriented regional technology sheet instead.
    ws=wb['7.6.CO_TEC_REG_FIJAS']
    header_row=None; header=[]
    for row_no,row in enumerate(ws.iter_rows(min_row=1,max_row=20,max_col=20,values_only=True),start=1):
        vals=[val(v) for v in row]
        joined=' | '.join(normalize(v) for v in vals)
        if 'tecnolog' in joined and 'conex' in joined and ('ano' in joined or 'año' in joined):
            header_row=row_no; header=vals; break
    if header_row is None:
        raise RuntimeError('Could not detect 7.6 technology header')

    idx={normalize(h):i for i,h in enumerate(header) if h}
    def find_key(fragment):
        matches=[(k,i) for k,i in idx.items() if fragment in k]
        if not matches: raise RuntimeError(f'Missing header fragment {fragment}: {header}')
        return matches[0][1]
    year_i=find_key('ano')
    month_i=find_key('mes')
    tech_i=find_key('tecnolog')
    conn_i=find_key('conex')
    region_i=find_key('region')

    current_year=None
    agg=defaultdict(lambda:{'connections':0,'regions':set(),'rows':0})
    for row_no,row in enumerate(ws.iter_rows(min_row=header_row+1,max_col=max(year_i,month_i,tech_i,conn_i,region_i)+1,values_only=True),start=header_row+1):
        vals=list(row)
        y=number(vals[year_i])
        if y is not None and 1990<=y<=2100: current_year=int(y)
        month=normalize(vals[month_i])[:3]
        if current_year!=2026 or month!='mar': continue
        tech=val(vals[tech_i]); conn=number(vals[conn_i]); region=val(vals[region_i])
        if not tech or conn is None: continue
        a=agg[tech]; a['connections']+=int(round(conn)); a['regions'].add(region); a['rows']+=1

    reg_rows=[]
    for tech,a in sorted(agg.items(),key=lambda kv:-kv[1]['connections']):
        reg_rows.append({'period':'2026-03','technology':tech,'connections':a['connections'],'region_count':len(a['regions']),'source_rows':a['rows'],'source_sheet':'7.6.CO_TEC_REG_FIJAS'})
    with REGIONAL_OUT.open('w',encoding='utf-8',newline='') as fh:
        f=['period','technology','connections','region_count','source_rows','source_sheet']
        w=csv.DictWriter(fh,fieldnames=f); w.writeheader(); w.writerows(reg_rows)

    print('national_sheet_rows',rows)
    print('regional_header_row',header_row,'header',header)
    print('regional_2026m03_technology',reg_rows,'sum',sum(r['connections'] for r in reg_rows))

if __name__=='__main__': main()
