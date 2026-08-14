#!/usr/bin/env python3
"""Integrate official SUBTEL March-2026 fixed-connection data into communal master.

Missing source communes remain missing. The derived intensity indicator is
residential fixed subscriptions per 100 Censo households; it is NOT a household
coverage rate and may exceed 100.
"""
from __future__ import annotations
import csv
from pathlib import Path

MASTER=Path('data/communal_master/chile_digital_inclusion_communes_2026_integrated.csv')
FIXED=Path('data/fixed_infrastructure_2026/commune_fixed_connections_2026_03.csv')
TMP=MASTER.with_suffix('.tmp.csv')

NEW=[
    'subtel_fixed_connections_total_2026m03',
    'subtel_fixed_connections_residential_2026m03',
    'subtel_fixed_residential_share_pct_2026m03',
    'subtel_fixed_residential_per_100_censo_households_2026m03',
    'subtel_fixed_source_status_2026m03',
]

def num(v):
    try:return float(v)
    except (TypeError,ValueError):return None

def main():
    with FIXED.open(encoding='utf-8') as f:
        fx={int(r['comuna']):r for r in csv.DictReader(f)}
    with MASTER.open(encoding='utf-8') as f:
        reader=csv.DictReader(f); base_fields=list(reader.fieldnames or []); rows=list(reader)
    fields=[x for x in base_fields if x not in NEW]+NEW
    missing=[]
    for r in rows:
        code=int(r['comuna']); x=fx.get(code,{})
        total=x.get('fixed_connections_total','')
        residential=x.get('fixed_connections_residential','')
        share=x.get('residential_share_pct','')
        status=x.get('source_status','source_not_reported')
        hh=num(r.get('hogares_total')); res=num(residential)
        intensity='' if hh in (None,0) or res is None else f'{res/hh*100:.4f}'
        r[NEW[0]]=total
        r[NEW[1]]=residential
        r[NEW[2]]=share
        r[NEW[3]]=intensity
        r[NEW[4]]=status
        if status!='reported':missing.append(code)
    with TMP.open('w',newline='',encoding='utf-8') as f:
        w=csv.DictWriter(f,fieldnames=fields); w.writeheader(); w.writerows(rows)
    TMP.replace(MASTER)
    print(f'master rows: {len(rows)}')
    print(f'master columns: {len(fields)}')
    print(f'SUBTEL source-not-reported communes: {len(missing)} {missing}')
    if len(rows)!=346 or len(missing)!=4:raise SystemExit('Unexpected fixed-layer integration QA')
if __name__=='__main__':main()
