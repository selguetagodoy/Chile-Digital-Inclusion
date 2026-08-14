#!/usr/bin/env python3
"""Integrate public SUBTEL 4G/5G point-record aggregates into the communal master."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

MASTER = Path('data/communal_master/chile_digital_inclusion_communes_2026_integrated.csv')
MOBILE = Path('data/mobile_coverage_2025/commune_mobile_network_points_2025_03.csv')

KEY = 'comuna'
MOBILE_PREFIXES = ('claro_', 'entel_', 'movistar_', 'wom_', 'mobile_4g_', 'mobile_5g_')


def main() -> None:
    master = pd.read_csv(MASTER)
    mobile = pd.read_csv(MOBILE)

    if len(master) != 346 or master[KEY].nunique() != 346:
        raise ValueError(f'Expected 346 unique communes in master, found {len(master)} rows / {master[KEY].nunique()} keys')
    if len(mobile) != 346 or mobile[KEY].nunique() != 346:
        raise ValueError(f'Expected 346 unique communes in mobile layer, found {len(mobile)} rows / {mobile[KEY].nunique()} keys')

    mobile_cols = [c for c in mobile.columns if c.startswith(MOBILE_PREFIXES)]
    if not mobile_cols:
        raise ValueError('No mobile point-record fields found')

    # Make the operation idempotent when the workflow is re-run.
    existing = [c for c in master.columns if c in mobile_cols]
    if existing:
        master = master.drop(columns=existing)

    merged = master.merge(mobile[[KEY] + mobile_cols], on=KEY, how='left', validate='one_to_one')
    if len(merged) != 346:
        raise ValueError(f'Merge changed commune row count to {len(merged)}')

    for col in mobile_cols:
        merged[col] = merged[col].fillna(0).astype(int)

    merged.to_csv(MASTER, index=False)

    print(f'Integrated {len(mobile_cols)} mobile-network fields')
    print(f'Master rows: {len(merged)}')
    print(f'Master columns: {len(merged.columns)}')
    print('5G records assigned:', int(merged['mobile_5g_point_records_2025m03'].sum()))
    print('4G records assigned:', int(merged['mobile_4g_point_records_2025m03'].sum()))
    print('Communes with >=1 5G record:', int((merged['mobile_5g_point_records_2025m03'] > 0).sum()))
    print('Communes with all 4 operators represented in 5G records:', int((merged['mobile_5g_operators_present_2025m03'] == 4).sum()))


if __name__ == '__main__':
    main()
