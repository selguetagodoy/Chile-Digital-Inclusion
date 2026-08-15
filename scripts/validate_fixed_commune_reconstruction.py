#!/usr/bin/env python3
"""Validate the reconciled SUBTEL March-2026 commune layer and master sync."""
from __future__ import annotations

import csv
from pathlib import Path

FIXED = Path('data/fixed_infrastructure_2026/commune_fixed_connections_2026_03.csv')
ALIGN = Path('data/fixed_infrastructure_2026/source_alignment_qa.csv')
MAP = Path('data/fixed_infrastructure_2026/source_row_mapping_2026_03.csv')
MISSING = Path('data/fixed_infrastructure_2026/source_not_reported_communes.csv')
MASTER = Path('data/communal_master/chile_digital_inclusion_communes_2026_integrated.csv')
EXPECTED_BLANK = {12202}


def rows(path: Path):
    with path.open(encoding='utf-8-sig', newline='') as fh:
        return list(csv.DictReader(fh))


def numeric_equal(a: str, b: str) -> bool:
    if (a or '') == '' and (b or '') == '':
        return True
    try:
        return abs(float(a) - float(b)) < 1e-9
    except (TypeError, ValueError):
        return False


def main() -> None:
    fixed = rows(FIXED)
    align = rows(ALIGN)
    mapping = rows(MAP)
    missing = rows(MISSING)
    master = rows(MASTER)

    if len(fixed) != 346 or len({r['comuna'] for r in fixed}) != 346:
        raise SystemExit(f'fixed layer shape invalid: rows={len(fixed)} unique={len({r["comuna"] for r in fixed})}')

    blank_codes = {int(r['comuna']) for r in fixed if r['source_status'] != 'reported'}
    if blank_codes != EXPECTED_BLANK:
        raise SystemExit(f'unexpected fixed source blanks: {sorted(blank_codes)}')

    if len(missing) != 1 or {int(r['comuna']) for r in missing} != EXPECTED_BLANK:
        raise SystemExit('source blank audit is not exactly Antártica (12202)')
    if {r.get('source_status') for r in missing} != {'source_blank'}:
        raise SystemExit('source blank audit has unexpected status')

    bad_align = [
        r for r in align
        if r.get('count_status') != 'pass'
        or r.get('subtotal_status') != 'pass'
        or r.get('label_order_status') != 'pass'
        or str(r.get('subtotal_delta')) not in {'0', '0.0'}
    ]
    if len(align) != 32 or bad_align:
        raise SystemExit(f'regional alignment invalid: checks={len(align)} failed={len(bad_align)}')

    if len(mapping) != 692:
        raise SystemExit(f'expected 692 row mappings (346 communes × 2 metrics), found {len(mapping)}')
    mapped_blank_codes = {
        int(r['mapped_commune']) for r in mapping
        if r.get('source_cell_status') == 'blank'
    }
    if mapped_blank_codes != EXPECTED_BLANK:
        raise SystemExit(f'unexpected mapped blank positions: {sorted(mapped_blank_codes)}')

    fixed_by_code = {r['comuna']: r for r in fixed}
    master_by_code = {r['comuna']: r for r in master}
    if set(fixed_by_code) != set(master_by_code):
        raise SystemExit('fixed layer and communal master do not contain the same commune codes')

    mismatches = []
    for code, src in fixed_by_code.items():
        dst = master_by_code[code]
        checks = [
            numeric_equal(src.get('fixed_connections_total', ''), dst.get('subtel_fixed_connections_total_2026m03', '')),
            numeric_equal(src.get('fixed_connections_residential', ''), dst.get('subtel_fixed_connections_residential_2026m03', '')),
            numeric_equal(src.get('residential_share_pct', ''), dst.get('subtel_fixed_residential_share_pct_2026m03', '')),
            src.get('source_status', '') == dst.get('subtel_fixed_source_status_2026m03', ''),
        ]
        if not all(checks):
            mismatches.append(code)

    if mismatches:
        raise SystemExit(f'fixed layer/master synchronization mismatches: {mismatches[:20]}')

    # Sentinel checks protect against the exact subtotal-as-commune regression
    # discovered in the original March-2026 extraction.
    sentinels = {
        '8303': 5656,   # Cabrero
        '8203': 5476,   # Cañete
        '9108': 8129,   # Lautaro
    }
    for code, expected in sentinels.items():
        actual = int(float(fixed_by_code[code]['fixed_connections_total']))
        if actual != expected:
            raise SystemExit(f'sentinel {code} changed unexpectedly: {actual} != {expected}')

    print('fixed_commune_reconstruction PASS')
    print('communes', len(fixed), 'numeric', 345, 'source_blank', sorted(blank_codes))
    print('regional_checks', len(align), 'row_mappings', len(mapping), 'master_mismatches', len(mismatches))


if __name__ == '__main__':
    main()
