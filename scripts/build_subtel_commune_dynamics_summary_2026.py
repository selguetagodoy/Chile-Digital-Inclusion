#!/usr/bin/env python3
from __future__ import annotations

import csv
import math
import statistics
from collections import Counter, defaultdict
from pathlib import Path

SRC = Path('data/fixed_infrastructure_2026/commune_fixed_connectivity_panel_2024_2026.csv')
OUT = Path('data/fixed_infrastructure_2026')


def num(v):
    if v in (None, ''):
        return None
    try:
        return float(v)
    except (TypeError, ValueError):
        return None


def write_csv(path: Path, rows: list[dict], fields: list[str] | None = None):
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        raise RuntimeError(f'No rows for {path}')
    fields = fields or list(rows[0].keys())
    with path.open('w', encoding='utf-8', newline='') as fh:
        w = csv.DictWriter(fh, fieldnames=fields)
        w.writeheader(); w.writerows(rows)


def pearson(xs, ys):
    if len(xs) != len(ys) or len(xs) < 2:
        return None
    mx, my = statistics.mean(xs), statistics.mean(ys)
    nume = sum((x-mx)*(y-my) for x, y in zip(xs, ys))
    denx = math.sqrt(sum((x-mx)**2 for x in xs))
    deny = math.sqrt(sum((y-my)**2 for y in ys))
    return nume / (denx * deny) if denx and deny else None


def ranks(values):
    order = sorted(range(len(values)), key=lambda i: values[i])
    result = [0.0] * len(values)
    i = 0
    while i < len(order):
        j = i
        val = values[order[i]]
        while j + 1 < len(order) and values[order[j + 1]] == val:
            j += 1
        avg_rank = (i + j + 2) / 2.0
        for k in range(i, j + 1):
            result[order[k]] = avg_rank
        i = j + 1
    return result


def spearman(xs, ys):
    return pearson(ranks(xs), ranks(ys))


def median(values):
    return statistics.median(values) if values else None


def mean(values):
    return statistics.mean(values) if values else None


def rural_band(v):
    if v < 20: return '0-<20% rural'
    if v < 40: return '20-<40% rural'
    if v < 60: return '40-<60% rural'
    if v < 80: return '60-<80% rural'
    return '80-100% rural'


def main():
    with SRC.open(encoding='utf-8') as fh:
        raw = list(csv.DictReader(fh))

    eligible = [r for r in raw if r['source_status_2026m06'] == 'reported' and int(float(r['censo_2024_households'])) >= 1000]
    if not eligible:
        raise RuntimeError('No eligible communes')

    corr_specs = [
        ('rurality_vs_fixed_intensity_2024', 'censo_2024_rural_households_pct', 'fixed_residential_per_100_censo_households_2024m06'),
        ('rurality_vs_fixed_intensity_2025', 'censo_2024_rural_households_pct', 'fixed_residential_per_100_censo_households_2025m06'),
        ('rurality_vs_fixed_intensity_2026', 'censo_2024_rural_households_pct', 'fixed_residential_per_100_censo_households_2026m06'),
        ('rurality_vs_intensity_change_2025_2026', 'censo_2024_rural_households_pct', 'fixed_residential_intensity_change_pp_2025m06_to_2026m06'),
        ('starting_intensity_2025_vs_change_2025_2026', 'fixed_residential_per_100_censo_households_2025m06', 'fixed_residential_intensity_change_pp_2025m06_to_2026m06'),
    ]
    corr_rows = []
    for name, xfield, yfield in corr_specs:
        pairs = [(num(r[xfield]), num(r[yfield])) for r in eligible]
        pairs = [(x, y) for x, y in pairs if x is not None and y is not None]
        xs, ys = [p[0] for p in pairs], [p[1] for p in pairs]
        corr_rows.append({
            'analysis': name, 'n_communes': len(pairs),
            'pearson_r': round(pearson(xs, ys), 6),
            'spearman_rho': round(spearman(xs, ys), 6),
            'scope': 'communes with >=1000 Censo 2024 households and reported SUBTEL values; descriptive association, not causal',
        })

    bands = defaultdict(list)
    for r in eligible:
        bands[rural_band(num(r['censo_2024_rural_households_pct']))].append(r)
    band_order = ['0-<20% rural','20-<40% rural','40-<60% rural','60-<80% rural','80-100% rural']
    band_rows = []
    for b in band_order:
        rs = bands[b]
        row = {'rurality_band': b, 'n_communes': len(rs)}
        for year in ('2024','2025','2026'):
            field = f'fixed_residential_per_100_censo_households_{year}m06'
            vals = [num(r[field]) for r in rs if num(r[field]) is not None]
            row[f'mean_fixed_intensity_{year}m06'] = round(mean(vals), 4)
            row[f'median_fixed_intensity_{year}m06'] = round(median(vals), 4)
        change = [num(r['fixed_residential_intensity_change_pp_2025m06_to_2026m06']) for r in rs]
        change = [v for v in change if v is not None]
        row['mean_intensity_change_pp_2025m06_to_2026m06'] = round(mean(change), 4)
        row['median_intensity_change_pp_2025m06_to_2026m06'] = round(median(change), 4)
        band_rows.append(row)

    thresholds = [10, 25, 50, 75]
    threshold_rows = []
    for year in ('2024','2025','2026'):
        field = f'fixed_residential_per_100_censo_households_{year}m06'
        vals = [(r, num(r[field])) for r in eligible]
        vals = [(r, v) for r, v in vals if v is not None]
        for t in thresholds:
            below = [r for r, v in vals if v < t]
            threshold_rows.append({
                'period': f'{year}-06', 'threshold_connections_per_100_households': t,
                'communes_below_threshold': len(below),
                'share_of_eligible_communes_pct': round(len(below)/len(vals)*100, 4),
            })

    def outlier_rows(field, direction, n=20):
        vals = [(r, num(r[field])) for r in eligible]
        vals = [(r, v) for r, v in vals if v is not None]
        vals.sort(key=lambda x: x[1], reverse=(direction == 'highest'))
        out = []
        for rank, (r, v) in enumerate(vals[:n], 1):
            out.append({
                'ranking': f'{direction}_{field}', 'rank': rank,
                'comuna': r['comuna'], 'comuna_nombre': r['comuna_nombre'], 'region_nombre': r['region_nombre'],
                'censo_2024_households': r['censo_2024_households'],
                'rural_households_pct': r['censo_2024_rural_households_pct'],
                'value': round(v, 4),
                'intensity_2024m06': r['fixed_residential_per_100_censo_households_2024m06'],
                'intensity_2025m06': r['fixed_residential_per_100_censo_households_2025m06'],
                'intensity_2026m06': r['fixed_residential_per_100_censo_households_2026m06'],
                'change_pp_2025m06_to_2026m06': r['fixed_residential_intensity_change_pp_2025m06_to_2026m06'],
            })
        return out

    outliers = []
    outliers += outlier_rows('fixed_residential_change_2025m06_to_2026m06', 'highest')
    outliers += outlier_rows('fixed_residential_change_2025m06_to_2026m06', 'lowest')
    outliers += outlier_rows('fixed_residential_intensity_change_pp_2025m06_to_2026m06', 'highest')
    outliers += outlier_rows('fixed_residential_intensity_change_pp_2025m06_to_2026m06', 'lowest')
    outliers += outlier_rows('fixed_residential_per_100_censo_households_2026m06', 'highest')
    outliers += outlier_rows('fixed_residential_per_100_censo_households_2026m06', 'lowest')

    low = [r for r in eligible if num(r['fixed_residential_per_100_censo_households_2026m06']) < 25]
    region_counts = Counter(r['region_nombre'] for r in low)
    regional_rows = []
    all_region_counts = Counter(r['region_nombre'] for r in eligible)
    for region, count in region_counts.most_common():
        regional_rows.append({
            'region_nombre': region,
            'communes_below_25_per_100_households': count,
            'eligible_communes_region': all_region_counts[region],
            'share_region_below_25_pct': round(count / all_region_counts[region] * 100, 4),
        })

    national_summary = []
    for year in ('2024','2025','2026'):
        field = f'fixed_residential_per_100_censo_households_{year}m06'
        vals = [num(r[field]) for r in eligible if num(r[field]) is not None]
        national_summary.append({
            'period': f'{year}-06', 'eligible_communes': len(vals),
            'mean_commune_fixed_intensity': round(mean(vals), 4),
            'median_commune_fixed_intensity': round(median(vals), 4),
            'p25_commune_fixed_intensity': round(statistics.quantiles(vals, n=4, method='inclusive')[0], 4),
            'p75_commune_fixed_intensity': round(statistics.quantiles(vals, n=4, method='inclusive')[2], 4),
        })

    write_csv(OUT/'commune_fixed_correlations_2024_2026.csv', corr_rows)
    write_csv(OUT/'commune_fixed_rurality_bands_2024_2026.csv', band_rows)
    write_csv(OUT/'commune_fixed_thresholds_2024_2026.csv', threshold_rows)
    write_csv(OUT/'commune_fixed_outliers_2025_2026.csv', outliers)
    write_csv(OUT/'commune_fixed_low_intensity_by_region_2026.csv', regional_rows)
    write_csv(OUT/'commune_fixed_distribution_summary_2024_2026.csv', national_summary)

    print('eligible_communes', len(eligible))
    print('correlations')
    for r in corr_rows: print(r)
    print('rurality_bands')
    for r in band_rows: print(r)
    print('thresholds')
    for r in threshold_rows: print(r)
    print('regions_below_25')
    for r in regional_rows: print(r)

if __name__ == '__main__':
    main()
