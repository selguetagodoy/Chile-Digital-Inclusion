#!/usr/bin/env python3
"""Integrate reconciled SUBTEL March-2026 fixed connections into the communal master.

The source workbook is reconstructed from formula-defined regional blocks. All
current communes receive numeric total/residential values except Antártica
(12202), whose source cell is explicitly blank and is preserved as source_blank.
The derived intensity indicator is residential fixed subscriptions per 100 Censo
households; it is NOT a household coverage rate and may exceed 100.
"""
from __future__ import annotations

import csv
from pathlib import Path

MASTER = Path('data/communal_master/chile_digital_inclusion_communes_2026_integrated.csv')
FIXED = Path('data/fixed_infrastructure_2026/commune_fixed_connections_2026_03.csv')
TMP = MASTER.with_suffix('.tmp.csv')
EXPECTED_NON_REPORTED = {12202}

NEW = [
    'subtel_fixed_connections_total_2026m03',
    'subtel_fixed_connections_residential_2026m03',
    'subtel_fixed_residential_share_pct_2026m03',
    'subtel_fixed_residential_per_100_censo_households_2026m03',
    'subtel_fixed_source_status_2026m03',
]


def num(v):
    try:
        return float(v)
    except (TypeError, ValueError):
        return None


def main():
    with FIXED.open(encoding='utf-8') as f:
        fixed_rows = list(csv.DictReader(f))
    fx = {int(r['comuna']): r for r in fixed_rows}

    if len(fixed_rows) != 346 or len(fx) != 346:
        raise SystemExit(f'Unexpected fixed source shape: rows={len(fixed_rows)} unique={len(fx)}')

    source_gaps = {int(r['comuna']) for r in fixed_rows if r.get('source_status') != 'reported'}
    if source_gaps != EXPECTED_NON_REPORTED:
        raise SystemExit(f'Unexpected source-gap set: {sorted(source_gaps)}')

    with MASTER.open(encoding='utf-8') as f:
        reader = csv.DictReader(f)
        base_fields = list(reader.fieldnames or [])
        rows = list(reader)

    fields = [x for x in base_fields if x not in NEW] + NEW
    missing = []
    for r in rows:
        code = int(r['comuna'])
        x = fx.get(code, {})
        total = x.get('fixed_connections_total', '')
        residential = x.get('fixed_connections_residential', '')
        share = x.get('residential_share_pct', '')
        status = x.get('source_status', 'source_missing')
        hh = num(r.get('hogares_total'))
        res = num(residential)
        intensity = '' if hh in (None, 0) or res is None else f'{res / hh * 100:.4f}'
        r[NEW[0]] = total
        r[NEW[1]] = residential
        r[NEW[2]] = share
        r[NEW[3]] = intensity
        r[NEW[4]] = status
        if status != 'reported':
            missing.append(code)

    with TMP.open('w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(rows)
    TMP.replace(MASTER)

    print(f'master rows: {len(rows)}')
    print(f'master columns: {len(fields)}')
    print(f'SUBTEL explicit source blanks: {len(missing)} {missing}')
    if len(rows) != 346 or set(missing) != EXPECTED_NON_REPORTED:
        raise SystemExit('Unexpected fixed-layer integration QA')


if __name__ == '__main__':
    main()
