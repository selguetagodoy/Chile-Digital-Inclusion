from __future__ import annotations

import csv
import io
import math
from pathlib import Path

import openpyxl
import requests

OUTDIR = Path('data/subtel_sector_series')

SOURCES = {
    'fixed': 'https://www.subtel.gob.cl/wp-content/uploads/2026/05/1_SERIES_CONEXIONES_INTERNET_FIJA_MAR26_040526.xlsx',
    'mobile': 'https://www.subtel.gob.cl/wp-content/uploads/2026/05/2_SERIES_CONEXIONES_INTERNET_MO%CC%81VIL-MAR26-040526.xlsx',
    'mobile_traffic': 'https://www.subtel.gob.cl/wp-content/uploads/2026/05/3_SERIES_TRAFICO_DATOS_MOVILES-MAR26-040526.xlsx',
    'fixed_traffic': 'https://www.subtel.gob.cl/wp-content/uploads/2026/05/3_SERIES_TRAFICO_DATOS_FIJOS-MAR26-040526.xlsx',
}

MONTHS = {
    'ene': 1, 'feb': 2, 'mar': 3, 'abr': 4, 'may': 5, 'jun': 6,
    'jul': 7, 'ago': 8, 'sep': 9, 'oct': 10, 'nov': 11, 'dic': 12,
}


def download(url: str) -> bytes:
    r = requests.get(url, timeout=180, allow_redirects=True)
    r.raise_for_status()
    if not r.content.startswith(b'PK'):
        raise RuntimeError(f'Expected XLSX from {url}; type={r.headers.get("content-type")} bytes={len(r.content)}')
    return r.content


def workbook(key: str):
    return openpyxl.load_workbook(io.BytesIO(download(SOURCES[key])), read_only=True, data_only=True)


def number(v):
    if v is None or v == '' or v == '---': return None
    if isinstance(v, bool): return None
    try:
        x = float(v)
        if math.isnan(x): return None
        return x
    except (TypeError, ValueError):
        return None


def integer(v):
    x = number(v)
    return None if x is None else int(round(x))


def month_no(v):
    if v is None: return None
    s = str(v).strip().lower().replace('.', '')[:3]
    return MONTHS.get(s)


def period(year: int, month: int) -> str:
    return f'{year:04d}-{month:02d}'


def iter_period_rows(ws, start_row: int, year_col: int, month_col: int, max_col: int):
    current_year = None
    for row_no, row in enumerate(ws.iter_rows(min_row=start_row, max_col=max_col, values_only=True), start=start_row):
        vals = list(row)
        y = integer(vals[year_col - 1]) if year_col <= len(vals) else None
        if y is not None and 1990 <= y <= 2100:
            current_year = y
        m = month_no(vals[month_col - 1]) if month_col <= len(vals) else None
        if current_year is None or m is None:
            continue
        yield row_no, current_year, m, vals


def write_csv(path: Path, rows: list[dict], fields: list[str]):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('w', encoding='utf-8', newline='') as fh:
        w = csv.DictWriter(fh, fieldnames=fields)
        w.writeheader(); w.writerows(rows)


def build_fixed():
    wb = workbook('fixed')

    total_rows = []
    ws = wb['7.1.CO_TOT_FIJAS']
    for row_no, y, m, v in iter_period_rows(ws, 9, 3, 4, 8):
        total = integer(v[4])
        if total is None: continue
        total_rows.append({
            'period': period(y,m), 'year': y, 'month': m,
            'fixed_connections_total': total,
            'annual_growth_pct': None if number(v[5]) is None else round(number(v[5])*100, 6),
            'penetration_per_100_inhabitants': None if number(v[6]) is None else round(number(v[6]), 6),
            'penetration_annual_change_pp': None if number(v[7]) is None else round(number(v[7]), 6),
            'source_sheet': '7.1.CO_TOT_FIJAS', 'source_row': row_no,
        })

    tech_rows = []
    ws = wb['7.7.CO_TEC_FIJAS']
    for row_no, y, m, v in iter_period_rows(ws, 7, 2, 3, 8):
        total = integer(v[3])
        if total is None: continue
        adsl, hfc, fiber, other = [integer(v[i]) for i in range(4,8)]
        fiber_share = (fiber / total * 100) if fiber is not None and total else None
        tech_rows.append({
            'period': period(y,m), 'year': y, 'month': m,
            'fixed_connections_total': total,
            'adsl_connections': adsl,
            'hfc_connections': hfc,
            'fttx_fiber_connections': fiber,
            'other_fixed_technology_connections': other,
            'fiber_share_pct': None if fiber_share is None else round(fiber_share, 6),
            'source_sheet': '7.7.CO_TEC_FIJAS', 'source_row': row_no,
        })

    return total_rows, tech_rows


def build_mobile():
    wb = workbook('mobile')
    rows = []
    ws = wb['8.1.CO_TEC_MOVIL']
    for row_no, y, m, v in iter_period_rows(ws, 8, 2, 3, 15):
        g2, g3, g4, g5 = [integer(v[i]) for i in range(3,7)]
        total = integer(v[7])
        broadband = integer(v[8])
        if total is None: continue
        rows.append({
            'period': period(y,m), 'year': y, 'month': m,
            'connections_2g': g2,
            'connections_3g': g3,
            'connections_4g': g4,
            'connections_5g': g5,
            'mobile_connections_total': total,
            'connections_3g_4g_5g': broadband,
            'penetration_2g_per_100': None if number(v[9]) is None else round(number(v[9]), 6),
            'penetration_3g_per_100': None if number(v[10]) is None else round(number(v[10]), 6),
            'penetration_4g_per_100': None if number(v[11]) is None else round(number(v[11]), 6),
            'penetration_5g_per_100': None if number(v[12]) is None else round(number(v[12]), 6),
            'penetration_3g_4g_5g_per_100': None if number(v[13]) is None else round(number(v[13]), 6),
            'penetration_total_per_100': None if number(v[14]) is None else round(number(v[14]), 6),
            'source_sheet': '8.1.CO_TEC_MOVIL', 'source_row': row_no,
        })
    return rows


def build_traffic(key: str, sheet: str, output_prefix: str):
    wb = workbook(key)
    rows=[]
    ws=wb[sheet]
    for row_no,y,m,v in iter_period_rows(ws,11,2,3,7):
        down=number(v[3]); up=number(v[4]); total=number(v[5]); growth=number(v[6])
        if total is None: continue
        rows.append({
            'period':period(y,m),'year':y,'month':m,
            f'{output_prefix}_downlink_tb':round(down,6) if down is not None else None,
            f'{output_prefix}_uplink_tb':round(up,6) if up is not None else None,
            f'{output_prefix}_total_tb':round(total,6),
            'annual_growth_pct':None if growth is None else round(growth*100,6),
            'source_sheet':sheet,'source_row':row_no,
        })
    return rows


def long_core(fixed_total, fixed_tech, mobile, mob_traf, fix_traf):
    rows=[]
    def add(source_rows, metrics, series_group, unit_map):
        for r in source_rows:
            for metric in metrics:
                value=r.get(metric)
                if value is None: continue
                rows.append({
                    'period':r['period'],'year':r['year'],'month':r['month'],
                    'series_group':series_group,'indicator':metric,'value':value,
                    'unit':unit_map.get(metric,''),'source_sheet':r['source_sheet'],'source_row':r['source_row'],
                })
    add(fixed_total,['fixed_connections_total','penetration_per_100_inhabitants'],'fixed_connections',{
        'fixed_connections_total':'connections','penetration_per_100_inhabitants':'per_100_inhabitants'})
    add(fixed_tech,['adsl_connections','hfc_connections','fttx_fiber_connections','other_fixed_technology_connections','fiber_share_pct'],'fixed_technology',{
        'adsl_connections':'connections','hfc_connections':'connections','fttx_fiber_connections':'connections','other_fixed_technology_connections':'connections','fiber_share_pct':'percent'})
    add(mobile,['connections_2g','connections_3g','connections_4g','connections_5g','mobile_connections_total','connections_3g_4g_5g'],'mobile_connections',{
        'connections_2g':'connections','connections_3g':'connections','connections_4g':'connections','connections_5g':'connections','mobile_connections_total':'connections','connections_3g_4g_5g':'connections'})
    add(mob_traf,['mobile_traffic_downlink_tb','mobile_traffic_uplink_tb','mobile_traffic_total_tb'],'mobile_traffic',{
        'mobile_traffic_downlink_tb':'TB','mobile_traffic_uplink_tb':'TB','mobile_traffic_total_tb':'TB'})
    add(fix_traf,['fixed_traffic_downlink_tb','fixed_traffic_uplink_tb','fixed_traffic_total_tb'],'fixed_traffic',{
        'fixed_traffic_downlink_tb':'TB','fixed_traffic_uplink_tb':'TB','fixed_traffic_total_tb':'TB'})
    return rows


def annual_snapshots(long_rows):
    # December observations for completed years. If a series has no December in
    # the first historical year, it is simply absent; no interpolation is used.
    return [r for r in long_rows if r['month']==12 and r['year']<=2025]


def qa(fixed_total, fixed_tech, mobile, mob_traf, fix_traf):
    groups={
        'fixed_connections':fixed_total,
        'fixed_technology':fixed_tech,
        'mobile_connections':mobile,
        'mobile_traffic':mob_traf,
        'fixed_traffic':fix_traf,
    }
    rows=[]
    for name,data in groups.items():
        periods=[r['period'] for r in data]
        rows += [
            {'check':f'{name}_rows','value':len(data),'expectation':'positive'},
            {'check':f'{name}_unique_periods','value':len(set(periods)),'expectation':str(len(data))},
            {'check':f'{name}_first_period','value':min(periods) if periods else '','expectation':'source-dependent'},
            {'check':f'{name}_last_period','value':max(periods) if periods else '','expectation':'2026-03'},
        ]

    # Cross-check published Q1 2026 snapshot already curated in the repo.
    latest_fixed=next(r for r in fixed_total if r['period']=='2026-03')
    latest_fixed_tech=next(r for r in fixed_tech if r['period']=='2026-03')
    latest_mobile=next(r for r in mobile if r['period']=='2026-03')
    rows += [
        {'check':'2026m03_fixed_total','value':latest_fixed['fixed_connections_total'],'expectation':'4859679'},
        {'check':'2026m03_fixed_total_tech_sheet','value':latest_fixed_tech['fixed_connections_total'],'expectation':'4859679'},
        {'check':'2026m03_5g_connections','value':latest_mobile['connections_5g'],'expectation':'10367754'},
        {'check':'2026m03_fiber_share_pct','value':latest_fixed_tech['fiber_share_pct'],'expectation':'approximately 85.3'},
    ]
    return rows


def main():
    OUTDIR.mkdir(parents=True,exist_ok=True)
    fixed_total,fixed_tech=build_fixed()
    mobile=build_mobile()
    mobile_traffic=build_traffic('mobile_traffic','9.1.TRAF_SENT','mobile_traffic')
    fixed_traffic=build_traffic('fixed_traffic','10.1.TRAF_SENT','fixed_traffic')

    write_csv(OUTDIR/'fixed_connections_monthly.csv',fixed_total,list(fixed_total[0].keys()))
    write_csv(OUTDIR/'fixed_technology_monthly.csv',fixed_tech,list(fixed_tech[0].keys()))
    write_csv(OUTDIR/'mobile_connections_by_technology_monthly.csv',mobile,list(mobile[0].keys()))
    write_csv(OUTDIR/'mobile_data_traffic_monthly.csv',mobile_traffic,list(mobile_traffic[0].keys()))
    write_csv(OUTDIR/'fixed_data_traffic_monthly.csv',fixed_traffic,list(fixed_traffic[0].keys()))

    long_rows=long_core(fixed_total,fixed_tech,mobile,mobile_traffic,fixed_traffic)
    write_csv(OUTDIR/'sector_core_monthly_long.csv',long_rows,list(long_rows[0].keys()))
    annual=annual_snapshots(long_rows)
    write_csv(OUTDIR/'sector_core_december_long_2000_2025.csv',annual,list(annual[0].keys()))

    qa_rows=qa(fixed_total,fixed_tech,mobile,mobile_traffic,fixed_traffic)
    write_csv(OUTDIR/'series_qa.csv',qa_rows,['check','value','expectation'])

    # Enforce load-bearing current controls.
    q={r['check']:str(r['value']) for r in qa_rows}
    if q['fixed_connections_last_period']!='2026-03' or q['mobile_connections_last_period']!='2026-03' or q['mobile_traffic_last_period']!='2026-03' or q['fixed_traffic_last_period']!='2026-03':
        raise RuntimeError('At least one official core series does not end in 2026-03')
    if int(float(q['2026m03_fixed_total'])) != 4859679:
        raise RuntimeError('Fixed connection total does not match Q1 2026 control')
    if int(float(q['2026m03_fixed_total_tech_sheet'])) != 4859679:
        raise RuntimeError('Fixed technology total does not reconcile to fixed total')
    if int(float(q['2026m03_5g_connections'])) != 10367754:
        raise RuntimeError('5G March 2026 does not match Q1 2026 control')
    fiber=float(q['2026m03_fiber_share_pct'])
    if not (85.2 <= fiber <= 85.4):
        raise RuntimeError(f'Fiber share outside expected Q1 2026 control: {fiber}')

    print('fixed_total',len(fixed_total),fixed_total[0]['period'],fixed_total[-1]['period'])
    print('fixed_tech',len(fixed_tech),fixed_tech[0]['period'],fixed_tech[-1]['period'])
    print('mobile',len(mobile),mobile[0]['period'],mobile[-1]['period'])
    print('mobile_traffic',len(mobile_traffic),mobile_traffic[0]['period'],mobile_traffic[-1]['period'])
    print('fixed_traffic',len(fixed_traffic),fixed_traffic[0]['period'],fixed_traffic[-1]['period'])
    print('long_rows',len(long_rows),'annual_december_rows',len(annual))

if __name__=='__main__':
    main()
