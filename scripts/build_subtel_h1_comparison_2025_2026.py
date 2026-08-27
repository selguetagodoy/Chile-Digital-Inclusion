#!/usr/bin/env python3
from __future__ import annotations

import csv
from pathlib import Path

DATA = Path('data/subtel_sector_series')
OUT = DATA / 'h1_market_dynamics_2025_2026.csv'

WINDOWS = {
    '1S2025': ('2024-12', '2025-06'),
    '1S2026': ('2025-12', '2026-06'),
}


def read(name):
    with (DATA/name).open(encoding='utf-8') as fh:
        return list(csv.DictReader(fh))


def num(v):
    if v in (None, ''): return None
    try: return float(v)
    except (TypeError, ValueError): return None


def pct(a,b):
    return (b/a-1)*100 if a not in (None,0) and b is not None else None


def add(rows, domain, metric, entity, data, value_field, share_field=None):
    idx={(r['period'],r.get('operator') or r.get('operator_group') or r.get('entity') or entity):r for r in data}
    for label,(p0,p1) in WINDOWS.items():
        key_entity=entity
        a=idx.get((p0,key_entity)); b=idx.get((p1,key_entity))
        if not a or not b: continue
        va,vb=num(a.get(value_field)),num(b.get(value_field))
        if va is None or vb is None: continue
        sa=num(a.get(share_field)) if share_field else None
        sb=num(b.get(share_field)) if share_field else None
        rows.append({
            'window':label,'domain':domain,'metric':metric,'entity':entity,
            'base_period':p0,'end_period':p1,'base_value':round(va,6),'end_value':round(vb,6),
            'absolute_change':round(vb-va,6),'pct_change':round(pct(va,vb),6) if pct(va,vb) is not None else '',
            'base_share_pct':round(sa,6) if sa is not None else '',
            'end_share_pct':round(sb,6) if sb is not None else '',
            'share_change_pp':round(sb-sa,6) if sa is not None and sb is not None else '',
        })


def add_single(rows, domain, metric, entity, data, value_field, share_field=None):
    idx={r['period']:r for r in data}
    for label,(p0,p1) in WINDOWS.items():
        a,b=idx.get(p0),idx.get(p1)
        if not a or not b: continue
        va,vb=num(a.get(value_field)),num(b.get(value_field))
        if va is None or vb is None: continue
        sa=num(a.get(share_field)) if share_field else None
        sb=num(b.get(share_field)) if share_field else None
        rows.append({
            'window':label,'domain':domain,'metric':metric,'entity':entity,
            'base_period':p0,'end_period':p1,'base_value':round(va,6),'end_value':round(vb,6),
            'absolute_change':round(vb-va,6),'pct_change':round(pct(va,vb),6) if pct(va,vb) is not None else '',
            'base_share_pct':round(sa,6) if sa is not None else '',
            'end_share_pct':round(sb,6) if sb is not None else '',
            'share_change_pp':round(sb-sa,6) if sa is not None and sb is not None else '',
        })


def main():
    rows=[]
    fixed=read('fixed_connections_monthly.csv')
    tech=read('mobile_connections_by_technology_monthly.csv')
    mplan=read('mobile_connections_by_plan_monthly.csv')
    mtraf=read('mobile_data_traffic_monthly.csv')
    ftraf=read('fixed_data_traffic_monthly.csv')
    sat=read('satellite_provider_dynamics_monthly.csv')
    mops=read('mobile_connections_by_operator_monthly.csv')
    mtops=read('mobile_traffic_by_operator_monthly.csv')
    fops=read('fixed_connections_by_operator_monthly.csv')
    ftops=read('fixed_traffic_by_group_monthly.csv')

    add_single(rows,'national','fixed_connections','all_fixed',fixed,'fixed_connections_total')
    add_single(rows,'mobile_technology','connections','4G',tech,'connections_4g')
    add_single(rows,'mobile_technology','connections','5G',tech,'connections_5g')
    add_single(rows,'mobile_plan','connections','prepaid',mplan,'prepaid_3g_4g_5g_connections','prepaid_share_3g_4g_5g_pct')
    add_single(rows,'mobile_plan','connections','contract',mplan,'contract_3g_4g_5g_connections','contract_share_3g_4g_5g_pct')
    add_single(rows,'traffic','mobile_total_tb','all_mobile',mtraf,'mobile_traffic_total_tb')
    add_single(rows,'traffic','fixed_total_tb','all_fixed',ftraf,'fixed_traffic_total_tb')
    add_single(rows,'satellite_proxy','connections','Starlink',sat,'starlink_connections','starlink_share_total_fixed_pct')
    add_single(rows,'satellite_proxy','connections','Hughesnet',sat,'hughesnet_connections')

    for op in ['Entel','Grupo Claro-VTR','Movistar','WOM']:
        add(rows,'mobile_operator','connections',op,mops,'connections','share_pct')
        add(rows,'mobile_operator','traffic_tb',op,mtops,'traffic_tb','share_pct')
    for op in ['Entel','GTD','Grupo Claro-VTR','Movistar','Mundo']:
        add(rows,'fixed_operator','connections',op,fops,'connections','share_pct')
        add(rows,'fixed_operator','traffic_tb',op,ftops,'traffic_tb','share_pct')

    # Add acceleration/deceleration comparing same metric/entity across H1 windows.
    lookup={(r['window'],r['domain'],r['metric'],r['entity']):r for r in rows}
    for r in rows:
        if r['window']!='1S2026': continue
        prev=lookup.get(('1S2025',r['domain'],r['metric'],r['entity']))
        if prev and prev['pct_change']!='' and r['pct_change']!='':
            r['pct_change_difference_vs_1S2025_pp']=round(float(r['pct_change'])-float(prev['pct_change']),6)
        else:
            r['pct_change_difference_vs_1S2025_pp']=''
    for r in rows:
        r.setdefault('pct_change_difference_vs_1S2025_pp','')

    fields=['window','domain','metric','entity','base_period','end_period','base_value','end_value','absolute_change','pct_change','base_share_pct','end_share_pct','share_change_pp','pct_change_difference_vs_1S2025_pp']
    with OUT.open('w',encoding='utf-8',newline='') as fh:
        w=csv.DictWriter(fh,fieldnames=fields); w.writeheader(); w.writerows(rows)
    print('rows',len(rows))
    for r in rows:
        if r['window']=='1S2026': print(r)

if __name__=='__main__': main()
