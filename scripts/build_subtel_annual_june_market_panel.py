#!/usr/bin/env python3
from __future__ import annotations

import csv
from pathlib import Path

DATA = Path('data/subtel_sector_series')


def read(name):
    with (DATA/name).open(encoding='utf-8') as fh:
        return list(csv.DictReader(fh))


def write(name, rows):
    if not rows: raise RuntimeError(name)
    with (DATA/name).open('w', encoding='utf-8', newline='') as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        w.writeheader(); w.writerows(rows)


def june(rows):
    return [r for r in rows if r.get('period','').endswith('-06')]


def main():
    fixed = {r['period']: r for r in read('fixed_connections_monthly.csv')}
    mobile_tech = {r['period']: r for r in read('mobile_connections_by_technology_monthly.csv')}
    mobile_plan = {r['period']: r for r in read('mobile_connections_by_plan_monthly.csv')}
    mobile_traffic = {r['period']: r for r in read('mobile_data_traffic_monthly.csv')}
    fixed_traffic = {r['period']: r for r in read('fixed_data_traffic_monthly.csv')}
    sat = {r['period']: r for r in read('satellite_provider_dynamics_monthly.csv')}
    intensity = {r['period']: r for r in read('mobile_plan_usage_intensity_monthly.csv')}

    periods = sorted({p for p in set(fixed)|set(mobile_tech)|set(mobile_plan)|set(mobile_traffic)|set(fixed_traffic)|set(sat) if p.endswith('-06')})
    national = []
    for p in periods:
        year = int(p[:4])
        f = fixed.get(p, {}); mt = mobile_tech.get(p, {}); mp = mobile_plan.get(p, {})
        mobt = mobile_traffic.get(p, {}); fixt = fixed_traffic.get(p, {}); s = sat.get(p, {}); ui = intensity.get(p, {})
        national.append({
            'period': p, 'year': year,
            'fixed_connections_total': f.get('fixed_connections_total',''),
            'fixed_penetration_per_100_people': f.get('fixed_penetration_per_100_people',''),
            'mobile_4g_connections': mt.get('connections_4g',''),
            'mobile_5g_connections': mt.get('connections_5g',''),
            'mobile_4g_minus_5g_gap': (int(float(mt['connections_4g']))-int(float(mt['connections_5g']))) if mt.get('connections_4g') and mt.get('connections_5g') else '',
            'mobile_5g_to_4g_ratio_pct': round(float(mt['connections_5g'])/float(mt['connections_4g'])*100,4) if mt.get('connections_4g') and mt.get('connections_5g') else '',
            'mobile_prepaid_connections_3g_4g_5g': mp.get('prepaid_3g_4g_5g_connections',''),
            'mobile_contract_connections_3g_4g_5g': mp.get('contract_3g_4g_5g_connections',''),
            'mobile_prepaid_share_pct': mp.get('prepaid_share_3g_4g_5g_pct',''),
            'mobile_contract_share_pct': mp.get('contract_share_3g_4g_5g_pct',''),
            'mobile_traffic_tb': mobt.get('mobile_traffic_total_tb',''),
            'fixed_traffic_tb': fixt.get('fixed_traffic_total_tb',''),
            'mobile_prepaid_gb_per_connection': ui.get('prepaid_gb_per_connection',''),
            'mobile_postpaid_gb_per_connection': ui.get('postpaid_gb_per_connection',''),
            'starlink_connections': s.get('starlink_connections',''),
            'hughesnet_connections': s.get('hughesnet_connections',''),
            'starlink_share_of_two_named_satellite_providers_pct': s.get('starlink_share_of_two_named_providers_pct',''),
            'starlink_share_total_fixed_pct': s.get('starlink_share_total_fixed_pct',''),
            'satellite_scope_note': s.get('scope_note','') if s else '',
        })
    write('annual_june_national_market_panel.csv', national)

    mob_ops = june(read('mobile_connections_by_operator_monthly.csv'))
    mob_traf = june(read('mobile_traffic_by_operator_monthly.csv'))
    mtraf = {(r['period'],r['operator']):r for r in mob_traf}
    mobile_rows=[]
    for r in mob_ops:
        tr=mtraf.get((r['period'],r['operator']),{})
        mobile_rows.append({
            'period':r['period'],'year':r['year'],'operator':r['operator'],'operator_source_label':r['operator_source_label'],
            'connections':r['connections'],'connection_share_pct':r['share_pct'],
            'traffic_tb':tr.get('traffic_tb',''),'traffic_share_pct':tr.get('share_pct',''),
        })
    write('annual_june_mobile_operator_panel.csv', mobile_rows)

    fix_ops = june(read('fixed_connections_by_operator_monthly.csv'))
    fix_traf = june(read('fixed_traffic_by_group_monthly.csv'))
    ftraf = {(r['period'],r['operator_group']):r for r in fix_traf}
    fixed_rows=[]
    for r in fix_ops:
        tr=ftraf.get((r['period'],r['operator']),{})
        fixed_rows.append({
            'period':r['period'],'year':r['year'],'operator':r['operator'],'operator_source_label':r['operator_source_label'],
            'connections':r['connections'],'connection_share_pct':r['share_pct'],
            'traffic_tb':tr.get('traffic_tb',''),'traffic_share_pct':tr.get('share_pct',''),
        })
    write('annual_june_fixed_operator_panel.csv', fixed_rows)

    print('national_june_rows',len(national))
    print('mobile_operator_june_rows',len(mobile_rows))
    print('fixed_operator_june_rows',len(fixed_rows))

if __name__ == '__main__': main()
