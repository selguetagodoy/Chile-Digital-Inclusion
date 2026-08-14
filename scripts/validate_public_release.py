#!/usr/bin/env python3
"""Validate structural integrity of the public Chile Digital Inclusion release."""

from __future__ import annotations

import csv
import json
from pathlib import Path

ROOT = Path('.')
MASTER = ROOT / 'data/communal_master/chile_digital_inclusion_communes_2026_integrated.csv'
GEO = ROOT / 'geo/chile_communes.geojson'
MOBILE = ROOT / 'data/mobile_coverage_2025/commune_mobile_network_points_2025_03.csv'
MOBILE_QA = ROOT / 'data/mobile_coverage_2025/spatial_assignment_coverage.csv'
SECTOR = ROOT / 'data/subtel_sector_2026/sector_snapshot_2026q1.csv'
OOKLA = ROOT / 'data/ookla/chile_2026q1_summary.csv'
INDEX = ROOT / 'index.html'
JS = ROOT / 'assets/dashboard.js'
CSS = ROOT / 'assets/dashboard.css'
REPORT = ROOT / 'data/metadata/public_release_validation.csv'

REQUIRED_MASTER = {
    'comuna', 'comuna_nombre', 'region', 'region_nombre',
    'hogares_total', 'hogares_sin_internet_pct', 'hogares_con_internet_fija_pct',
    'mobile_4g_point_records_2025m03', 'mobile_4g_operators_present_2025m03',
    'mobile_5g_point_records_2025m03', 'mobile_5g_operators_present_2025m03',
    'ookla_fixed_download_mbps_2026q1', 'ookla_mobile_download_mbps_2026q1',
}
REQUIRED_SECTOR = {
    'accesses_5g', 'fiber_share_fixed_connections',
    'fixed_household_penetration_national', 'fixed_household_penetration_rural',
}
REQUIRED_DOM_IDS = {
    'map', 'indicator', 'commune-search', 'data-status', 'ranking-body', 'detail-grid',
    'kpi-households', 'kpi-disconnected', 'kpi-fixed', 'kpi-computer',
    'kpi-sector-5g', 'kpi-sector-fiber', 'kpi-sector-fixed-households', 'kpi-sector-rural-fixed',
}


def read_csv(path: Path):
    with path.open(encoding='utf-8-sig', newline='') as fh:
        return list(csv.DictReader(fh))


def check(name: str, condition: bool, detail: str) -> dict:
    return {'check': name, 'status': 'PASS' if condition else 'FAIL', 'detail': detail}


def main() -> None:
    results = []
    required_files = [MASTER, GEO, MOBILE, MOBILE_QA, SECTOR, OOKLA, INDEX, JS, CSS]
    for path in required_files:
        results.append(check(f'file:{path}', path.exists(), 'required public file exists'))

    master = read_csv(MASTER)
    master_fields = set(master[0].keys()) if master else set()
    master_codes = [int(r['comuna']) for r in master]
    results.append(check('master_rows', len(master) == 346, f'{len(master)} commune rows'))
    results.append(check('master_unique_communes', len(set(master_codes)) == 346, f'{len(set(master_codes))} unique commune codes'))
    results.append(check('master_columns', len(master_fields) == 77, f'{len(master_fields)} variables'))
    missing_master = sorted(REQUIRED_MASTER - master_fields)
    results.append(check('master_required_fields', not missing_master, f'missing={missing_master}'))

    mobile = read_csv(MOBILE)
    results.append(check('mobile_rows', len(mobile) == 346, f'{len(mobile)} commune rows'))
    results.append(check('mobile_unique_communes', len({int(r["comuna"]) for r in mobile}) == 346, '346 unique commune codes expected'))

    mobile_qa = read_csv(MOBILE_QA)
    total = sum(int(r['total_point_records']) for r in mobile_qa)
    assigned = sum(int(r['assigned_to_commune']) for r in mobile_qa)
    assigned_pct = assigned / total * 100 if total else 0
    results.append(check('mobile_spatial_assignment', assigned_pct >= 99.5, f'{assigned}/{total} = {assigned_pct:.4f}% assigned'))

    with GEO.open(encoding='utf-8') as fh:
        geo = json.load(fh)
    features = geo.get('features', [])
    geo_codes = {int(f['properties']['commune_code']) for f in features}
    results.append(check('geo_features', len(features) == 345, f'{len(features)} BCN commune polygons'))
    results.append(check('geo_codes_in_master', geo_codes.issubset(set(master_codes)), f'{len(geo_codes)} geometry codes found in master'))

    sector = read_csv(SECTOR)
    sector_indicators = {r['indicator'] for r in sector}
    missing_sector = sorted(REQUIRED_SECTOR - sector_indicators)
    results.append(check('sector_required_indicators', not missing_sector, f'missing={missing_sector}'))

    ookla = read_csv(OOKLA)
    networks = {r['network'] for r in ookla}
    results.append(check('ookla_networks', networks == {'fixed', 'mobile'}, f'networks={sorted(networks)}'))

    html = INDEX.read_text(encoding='utf-8')
    missing_ids = sorted(dom_id for dom_id in REQUIRED_DOM_IDS if f'id="{dom_id}"' not in html)
    results.append(check('dashboard_dom_contract', not missing_ids, f'missing_ids={missing_ids}'))

    js = JS.read_text(encoding='utf-8')
    for ref in [
        'chile_digital_inclusion_communes_2026_integrated.csv',
        'chile_communes.geojson',
        'sector_snapshot_2026q1.csv',
        'mobile_5g_operators_present_2025m03',
    ]:
        results.append(check(f'dashboard_reference:{ref}', ref in js, 'dashboard references expected data/field'))

    REPORT.parent.mkdir(parents=True, exist_ok=True)
    with REPORT.open('w', encoding='utf-8', newline='') as fh:
        writer = csv.DictWriter(fh, fieldnames=['check', 'status', 'detail'])
        writer.writeheader()
        writer.writerows(results)

    failed = [r for r in results if r['status'] != 'PASS']
    print(f'Validation checks: {len(results)} | failed: {len(failed)}')
    for row in results:
        print(row['status'], row['check'], '-', row['detail'])
    if failed:
        raise SystemExit(1)


if __name__ == '__main__':
    main()
