#!/usr/bin/env python3

import csv
from pathlib import Path

from build_ookla_chile_quarter import build_period, load_chile_geometry

OUTPUT = Path('data/ookla/chile_2024q1_2026q2_longitudinal.csv')
PERIODS = [(2024, 1), (2024, 2), (2024, 3), (2024, 4),
           (2025, 1), (2025, 2), (2025, 3), (2025, 4),
           (2026, 1), (2026, 2)]


def pct_change(old, new):
    if old in (None, 0):
        return ''
    return round((new - old) / old * 100.0, 3)


def main():
    chile = load_chile_geometry()
    rows = []
    previous = {}

    for year, quarter in PERIODS:
        summary, _ = build_period(year, quarter, chile, OUTPUT.parent, keep_tiles=False)
        for row in summary:
            network = row['network']
            prev = previous.get(network)
            out = {
                'period': f'{year}Q{quarter}',
                'year': year,
                'quarter': quarter,
                'network': network,
                'tiles': row['tiles'],
                'tests': row['tests'],
                'download_mbps_test_weighted': row['download_mbps_test_weighted'],
                'upload_mbps_test_weighted': row['upload_mbps_test_weighted'],
                'latency_ms_test_weighted': row['latency_ms_test_weighted'],
                'loaded_latency_down_ms_test_weighted': row['loaded_latency_down_ms_test_weighted'],
                'loaded_latency_up_ms_test_weighted': row['loaded_latency_up_ms_test_weighted'],
                'download_qoq_pct': pct_change(prev['download_mbps_test_weighted'], row['download_mbps_test_weighted']) if prev else '',
                'upload_qoq_pct': pct_change(prev['upload_mbps_test_weighted'], row['upload_mbps_test_weighted']) if prev else '',
                'latency_qoq_pct': pct_change(prev['latency_ms_test_weighted'], row['latency_ms_test_weighted']) if prev else '',
                'aggregation': row['aggregation'],
                'spatial_filter': row['spatial_filter'],
                'source_url': row['source_url'],
            }
            rows.append(out)
            previous[network] = row

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    with OUTPUT.open('w', encoding='utf-8', newline='') as fh:
        writer = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)

    print(f'Wrote {OUTPUT} with {len(rows)} rows')
    for network in ('fixed', 'mobile'):
        print(network)
        for r in rows:
            if r['network'] == network:
                print(r['period'], r['download_mbps_test_weighted'], r['tests'])


if __name__ == '__main__':
    main()
