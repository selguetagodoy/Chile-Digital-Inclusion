from __future__ import annotations

import csv
from collections import defaultdict
from datetime import date
from pathlib import Path

DATA = Path('data/subtel_sector_series')


def read_csv(name: str) -> list[dict]:
    with (DATA / name).open(encoding='utf-8') as fh:
        return list(csv.DictReader(fh))


def num(v):
    if v in (None, ''):
        return None
    try:
        return float(v)
    except (TypeError, ValueError):
        return None


def write_csv(name: str, rows: list[dict], fields: list[str]):
    with (DATA / name).open('w', encoding='utf-8', newline='') as fh:
        w = csv.DictWriter(fh, fieldnames=fields)
        w.writeheader()
        w.writerows(rows)


def add_months(period: str, months: float) -> str:
    """Return an approximate year-month label for a fractional-month horizon."""
    y, m = map(int, period.split('-'))
    whole = int(months)
    frac = months - whole
    idx = y * 12 + (m - 1) + whole
    yy, mm0 = divmod(idx, 12)
    # >= half a month rounds into the following month for a conservative label.
    if frac >= 0.5:
        mm0 += 1
        if mm0 == 12:
            yy += 1
            mm0 = 0
    return f'{yy:04d}-{mm0 + 1:02d}'


def build_plan_intensity():
    plans = {r['period']: r for r in read_csv('mobile_connections_by_plan_monthly.csv')}
    traffic = {r['period']: r for r in read_csv('mobile_traffic_by_plan_monthly.csv')}
    periods = sorted(set(plans) & set(traffic))
    out = []
    for p in periods:
        a, t = plans[p], traffic[p]
        prepaid_conn = num(a['prepaid_3g_4g_5g_connections'])
        postpaid_conn = num(a['contract_3g_4g_5g_connections'])
        prepaid_tb = num(t['prepaid_traffic_tb'])
        postpaid_tb = num(t['postpaid_traffic_tb'])
        prepaid_gb = prepaid_tb * 1000 / prepaid_conn if prepaid_conn else None
        postpaid_gb = postpaid_tb * 1000 / postpaid_conn if postpaid_conn else None
        out.append({
            'period': p,
            'prepaid_connections_3g_4g_5g': int(prepaid_conn) if prepaid_conn is not None else '',
            'postpaid_connections_3g_4g_5g': int(postpaid_conn) if postpaid_conn is not None else '',
            'prepaid_traffic_tb': round(prepaid_tb, 6) if prepaid_tb is not None else '',
            'postpaid_traffic_tb': round(postpaid_tb, 6) if postpaid_tb is not None else '',
            'prepaid_gb_per_connection': round(prepaid_gb, 4) if prepaid_gb is not None else '',
            'postpaid_gb_per_connection': round(postpaid_gb, 4) if postpaid_gb is not None else '',
            'postpaid_to_prepaid_usage_ratio': round(postpaid_gb / prepaid_gb, 4) if prepaid_gb else '',
            'conversion_note': '1 TB = 1000 GB; descriptive monthly traffic divided by active 3G+4G+5G connections',
        })
    return out


def pct_change(a, b):
    return (b / a - 1) * 100 if a not in (None, 0) and b is not None else None


def build_mobile_operator_scatter():
    conn_rows = read_csv('mobile_connections_by_operator_monthly.csv')
    traf_rows = read_csv('mobile_traffic_by_operator_monthly.csv')
    major = {'Entel', 'Grupo Claro-VTR', 'Movistar', 'WOM'}
    conn = {(r['period'], r['operator']): r for r in conn_rows if r['operator'] in major}
    traf = {(r['period'], r['operator']): r for r in traf_rows if r['operator'] in major}
    comparisons = [('2024-06', '2025-06'), ('2025-06', '2026-06'), ('2025-12', '2026-06')]
    out = []
    for base, end in comparisons:
        for op in sorted(major):
            ca, cb = conn.get((base, op)), conn.get((end, op))
            ta, tb = traf.get((base, op)), traf.get((end, op))
            if not all((ca, cb, ta, tb)):
                continue
            c0, c1 = num(ca['connections']), num(cb['connections'])
            t0, t1 = num(ta['traffic_tb']), num(tb['traffic_tb'])
            out.append({
                'base_period': base, 'end_period': end, 'operator': op,
                'connections_base': int(c0), 'connections_end': int(c1),
                'connections_growth_pct': round(pct_change(c0, c1), 6),
                'traffic_tb_base': round(t0, 6), 'traffic_tb_end': round(t1, 6),
                'traffic_growth_pct': round(pct_change(t0, t1), 6),
                'connection_share_end_pct': round(num(cb['share_pct']), 6),
                'traffic_share_end_pct': round(num(tb['share_pct']), 6),
                'traffic_minus_connections_growth_pp': round(pct_change(t0, t1) - pct_change(c0, c1), 6),
            })
    return out


def build_fixed_group_traffic():
    raw = read_csv('fixed_traffic_by_operator_monthly.csv')
    mapping = {
        'Entel': 'Entel', 'Entelphone': 'Entel',
        'Telsur': 'GTD', 'GTD Manquehue': 'GTD',
        'Grupo Claro-VTR': 'Grupo Claro-VTR',
        'Movistar': 'Movistar',
        'Mundo Pacífico': 'Mundo',
    }
    sums = defaultdict(float)
    totals = {}
    for r in raw:
        group = mapping.get(r['operator'])
        if not group:
            continue
        p = r['period']
        sums[(p, group)] += num(r['traffic_tb']) or 0
        totals[p] = num(r['total_market_tb'])
    out = []
    for (p, group), value in sorted(sums.items()):
        total = totals[p]
        out.append({
            'period': p, 'operator_group': group,
            'traffic_tb': round(value, 6),
            'total_market_tb': round(total, 6) if total is not None else '',
            'share_pct': round(value / total * 100, 6) if total else '',
            'aggregation_note': 'Entel=Entel S.A.+Entelphone; GTD=Telsur+GTD Manquehue; other groups preserve source label',
        })
    return out


def build_fixed_operator_scatter(group_traffic):
    conn_rows = read_csv('fixed_connections_by_operator_monthly.csv')
    major = {'Entel', 'GTD', 'Grupo Claro-VTR', 'Movistar', 'Mundo'}
    conn = {(r['period'], r['operator']): r for r in conn_rows if r['operator'] in major}
    traf = {(r['period'], r['operator_group']): r for r in group_traffic if r['operator_group'] in major}
    comparisons = [('2024-06', '2025-06'), ('2025-06', '2026-06'), ('2025-12', '2026-06')]
    out = []
    for base, end in comparisons:
        for op in sorted(major):
            ca, cb = conn.get((base, op)), conn.get((end, op))
            ta, tb = traf.get((base, op)), traf.get((end, op))
            if not all((ca, cb, ta, tb)):
                continue
            c0, c1 = num(ca['connections']), num(cb['connections'])
            t0, t1 = num(ta['traffic_tb']), num(tb['traffic_tb'])
            out.append({
                'base_period': base, 'end_period': end, 'operator': op,
                'connections_base': int(c0), 'connections_end': int(c1),
                'connections_growth_pct': round(pct_change(c0, c1), 6),
                'traffic_tb_base': round(t0, 6), 'traffic_tb_end': round(t1, 6),
                'traffic_growth_pct': round(pct_change(t0, t1), 6),
                'connection_share_end_pct': round(num(cb['share_pct']), 6),
                'traffic_share_end_pct': round(num(tb['share_pct']), 6),
                'traffic_minus_connections_growth_pp': round(pct_change(t0, t1) - pct_change(c0, c1), 6),
            })
    return out


def build_satellite_dynamics():
    raw = read_csv('fixed_satellite_operator_connections_monthly.csv')
    by_period = defaultdict(dict)
    total_market = {}
    for r in raw:
        p = r['period']
        by_period[p][r['operator']] = num(r['connections']) or 0
        total_market[p] = num(r['total_fixed_market'])
    out = []
    for p in sorted(by_period):
        hughes = by_period[p].get('Hughesnet', 0)
        starlink = by_period[p].get('Starlink', 0)
        combined = hughes + starlink
        market = total_market[p]
        out.append({
            'period': p,
            'hughesnet_connections': int(hughes),
            'starlink_connections': int(starlink),
            'two_named_satellite_providers_connections': int(combined),
            'starlink_share_of_two_named_providers_pct': round(starlink / combined * 100, 6) if combined else '',
            'two_named_providers_share_total_fixed_pct': round(combined / market * 100, 6) if market else '',
            'starlink_share_total_fixed_pct': round(starlink / market * 100, 6) if market else '',
            'scope_note': 'Operator proxy using Hughesnet and Starlink only; not a complete technology-total measure of satellite access',
        })
    return out


def build_4g5g_convergence():
    raw = read_csv('mobile_connections_by_technology_monthly.csv')
    rows = []
    for r in raw:
        g4, g5 = num(r.get('connections_4g')), num(r.get('connections_5g'))
        if g4 is None or g5 is None:
            continue
        rows.append({
            'period': r['period'], 'connections_4g': int(g4), 'connections_5g': int(g5),
            'gap_4g_minus_5g': int(round(g4 - g5)),
            'ratio_5g_to_4g_pct': round(g5 / g4 * 100, 6) if g4 else '',
        })
    rows.sort(key=lambda x: x['period'])
    prev_gap = None
    closures = []
    for r in rows:
        gap = r['gap_4g_minus_5g']
        closure = '' if prev_gap is None else prev_gap - gap
        r['gap_closure_vs_prior_month'] = closure
        if closure != '':
            closures.append((r['period'], closure))
        last3 = [v for p, v in closures if p <= r['period']][-3:]
        r['trailing_3m_avg_gap_closure'] = round(sum(last3) / len(last3), 3) if last3 else ''
        prev_gap = gap

    by_period = {r['period']: r for r in rows}
    summary = []
    semesters = [
        ('1S2025', '2024-12', '2025-06', 6),
        ('2S2025', '2025-06', '2025-12', 6),
        ('1S2026', '2025-12', '2026-06', 6),
    ]
    for label, base, end, intervals in semesters:
        if base not in by_period or end not in by_period:
            continue
        start_gap = by_period[base]['gap_4g_minus_5g']
        end_gap = by_period[end]['gap_4g_minus_5g']
        closure = start_gap - end_gap
        avg = closure / intervals
        summary.append({
            'window': label, 'base_period': base, 'end_period': end,
            'gap_base': start_gap, 'gap_end': end_gap,
            'gap_closed': closure, 'avg_gap_closure_per_month': round(avg, 3),
        })

    latest = by_period.get('2026-06')
    if latest:
        h1 = next((r for r in summary if r['window'] == '1S2026'), None)
        rate_h1 = num(h1['avg_gap_closure_per_month']) if h1 else None
        rate_3m = num(latest['trailing_3m_avg_gap_closure'])
        for method, rate in [('1S2026_average', rate_h1), ('trailing_3m_average', rate_3m)]:
            months = latest['gap_4g_minus_5g'] / rate if rate and rate > 0 else None
            summary.append({
                'window': f'crossover_projection_{method}', 'base_period': '2026-06', 'end_period': '',
                'gap_base': latest['gap_4g_minus_5g'], 'gap_end': '', 'gap_closed': '',
                'avg_gap_closure_per_month': round(rate, 3) if rate else '',
                'months_to_crossover_from_june_2026': round(months, 3) if months is not None else '',
                'mechanical_crossover_month': add_months('2026-06', months) if months is not None else '',
                'projection_note': 'Mechanical linear extrapolation; not a forecast',
            })
    return rows, summary


def main():
    intensity = build_plan_intensity()
    mobile_scatter = build_mobile_operator_scatter()
    fixed_group_traffic = build_fixed_group_traffic()
    fixed_scatter = build_fixed_operator_scatter(fixed_group_traffic)
    satellite = build_satellite_dynamics()
    convergence, convergence_summary = build_4g5g_convergence()

    write_csv('mobile_plan_usage_intensity_monthly.csv', intensity, list(intensity[0]))
    write_csv('mobile_operator_connections_vs_traffic_growth.csv', mobile_scatter, list(mobile_scatter[0]))
    write_csv('fixed_traffic_by_group_monthly.csv', fixed_group_traffic, list(fixed_group_traffic[0]))
    write_csv('fixed_operator_connections_vs_traffic_growth.csv', fixed_scatter, list(fixed_scatter[0]))
    write_csv('satellite_provider_dynamics_monthly.csv', satellite, list(satellite[0]))
    write_csv('mobile_4g_5g_convergence_monthly.csv', convergence, list(convergence[0]))
    fields = sorted({k for r in convergence_summary for k in r})
    ordered = ['window', 'base_period', 'end_period', 'gap_base', 'gap_end', 'gap_closed', 'avg_gap_closure_per_month', 'months_to_crossover_from_june_2026', 'mechanical_crossover_month', 'projection_note']
    write_csv('mobile_4g_5g_convergence_summary.csv', convergence_summary, [f for f in ordered if f in fields])

    print('usage_intensity_rows', len(intensity))
    print('mobile_scatter_rows', len(mobile_scatter))
    print('fixed_group_traffic_rows', len(fixed_group_traffic))
    print('fixed_scatter_rows', len(fixed_scatter))
    print('satellite_rows', len(satellite))
    print('convergence_rows', len(convergence))
    print('convergence_summary_rows', len(convergence_summary))


if __name__ == '__main__':
    main()
