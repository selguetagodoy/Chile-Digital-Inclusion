from __future__ import annotations

import csv
import io
from pathlib import Path
import openpyxl
import requests

URL='https://www.subtel.gob.cl/wp-content/uploads/2026/05/2_SERIES_CONEXIONES_INTERNET_MO%CC%81VIL-MAR26-040526.xlsx'
OUT=Path('data/subtel_sector_series/latest_mobile_row_audit.csv')


def main():
    r=requests.get(URL,timeout=180); r.raise_for_status()
    wb=openpyxl.load_workbook(io.BytesIO(r.content),read_only=True,data_only=True)
    ws=wb['8.1.CO_TEC_MOVIL']
    rows=[]; current_year=None
    for row_no,row in enumerate(ws.iter_rows(min_row=8,max_col=15,values_only=True),start=8):
        vals=list(row)
        if vals[1] is not None:
            try:
                y=int(float(vals[1]))
                if 1990<=y<=2100: current_year=y
            except Exception: pass
        month='' if vals[2] is None else str(vals[2]).strip()
        if current_year==2026 and month:
            rows.append({
                'source_row':row_no,'year':current_year,'month':month,
                'col4_2g':vals[3],'col5_3g':vals[4],'col6_4g':vals[5],'col7_5g':vals[6],
                'col8_total':vals[7],'col9_3g4g5g':vals[8],
                'col10_pen2g':vals[9],'col11_pen3g':vals[10],'col12_pen4g':vals[11],'col13_pen5g':vals[12],
                'col14_pen345':vals[13],'col15_pen_total':vals[14],
            })
    OUT.parent.mkdir(parents=True,exist_ok=True)
    fields=list(rows[0].keys())
    with OUT.open('w',encoding='utf-8',newline='') as fh:
        w=csv.DictWriter(fh,fieldnames=fields); w.writeheader(); w.writerows(rows)
    print(rows)

if __name__=='__main__': main()
