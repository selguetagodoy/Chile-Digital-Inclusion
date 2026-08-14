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
FIXED = ROOT / 'data/fixed_access_infrastructure/commune_fixed_access_presence.csv'
FIXED_QA = ROOT / 'data/fixed_access_infrastructure/presence_query_qa.csv'
FIXED_SUB = ROOT / 'data/fixed_infrastructure_2026/commune_fixed_connections_2026_03.csv'
FIXED_SUB_QA = ROOT / 'data/fixed_infrastructure_2026/source_match_qa.csv'
FIXED_SUB_MISSING = ROOT / 'data/fixed_infrastructure_2026/source_not_reported_communes.csv'
SECTOR = ROOT / 'data/subtel_sector_2026/sector_snapshot_2026q1.csv'
OOKLA = ROOT / 'data/ookla/chile_2026q1_summary.csv'
EDU_EST = ROOT / 'data/education_connectivity_2026/aulas_conectadas_2025_establishments.csv'
EDU_ENRICHED = ROOT / 'data/education_connectivity_2026/aulas_conectadas_2025_establishments_enriched.csv'
EDU_COMMUNES = ROOT / 'data/education_connectivity_2026/aulas_conectadas_2025_commune_summary.csv'
EDU_QA = ROOT / 'data/education_connectivity_2026/aulas_conectadas_2025_crosswalk_qa.csv'
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
    'mineduc_aulas_selected_establishments_2025',
    'mineduc_aulas_waitlist_establishments_2025',
    'mineduc_aulas_selected_rural_establishments_2025',
    'mineduc_aulas_selected_enrollment_2025',
    'mineduc_aulas_selected_with_coordinates_2025',
    'fixed_access_public_layers_present',
    'fixed_access_public_operators_present',
    'subtel_fixed_connections_total_2026m03',
    'subtel_fixed_connections_residential_2026m03',
    'subtel_fixed_residential_share_pct_2026m03',
    'subtel_fixed_residential_per_100_censo_households_2026m03',
    'subtel_fixed_source_status_2026m03',
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


def qa_value(rows, metric):
    row = next((r for r in rows if r.get('metric') == metric), None)
    return row.get('value') if row else None


def main() -> None:
    results = []
    required_files = [MASTER, GEO, MOBILE, MOBILE_QA, FIXED, FIXED_QA, FIXED_SUB, FIXED_SUB_QA, FIXED_SUB_MISSING, SECTOR, OOKLA, EDU_EST, EDU_ENRICHED, EDU_COMMUNES, EDU_QA, INDEX, JS, CSS]
    for path in required_files:
        results.append(check(f'file:{path}', path.exists(), 'required public file exists'))

    master = read_csv(MASTER)
    master_fields = set(master[0].keys()) if master else set()
    master_codes = [int(r['comuna']) for r in master]
    results.append(check('master_rows', len(master) == 346, f'{len(master)} commune rows'))
    results.append(check('master_unique_communes', len(set(master_codes)) == 346, f'{len(set(master_codes))} unique commune codes'))
    results.append(check('master_columns', len(master_fields) == 89, f'{len(master_fields)} variables'))
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

    fixed = read_csv(FIXED)
    fixed_codes = {int(r['comuna']) for r in fixed}
    fixed_present = sum(int(r['fixed_access_public_layers_present']) > 0 for r in fixed)
    fixed_max_operators = max(int(r['fixed_access_public_operators_present']) for r in fixed)
    results.append(check('fixed_presence_rows', len(fixed) == 346, f'{len(fixed)} commune rows'))
    results.append(check('fixed_presence_unique_communes', len(fixed_codes) == 346, f'{len(fixed_codes)} unique commune codes'))
    results.append(check('fixed_presence_communes', fixed_present == 307, f'{fixed_present} communes with at least one public RedAcceso layer'))
    results.append(check('fixed_presence_max_operators', fixed_max_operators == 4, f'max operators/entities present={fixed_max_operators}'))

    fixed_qa = read_csv(FIXED_QA)
    fixed_bad = [r for r in fixed_qa if r['status'] not in {'ok', 'no_commune_geometry'}]
    results.append(check('fixed_presence_queries', len(fixed_qa) == 2076, f'{len(fixed_qa)} commune × layer queries'))
    results.append(check('fixed_presence_query_failures', not fixed_bad, f'failed={len(fixed_bad)}'))

    fixed_sub = read_csv(FIXED_SUB)
    fixed_sub_reported = sum(r['source_status'] == 'reported' for r in fixed_sub)
    fixed_sub_unmatched = read_csv(FIXED_SUB_QA)
    fixed_sub_missing = read_csv(FIXED_SUB_MISSING)
    results.append(check('fixed_subscription_rows', len(fixed_sub) == 346, f'{len(fixed_sub)} commune rows'))
    results.append(check('fixed_subscription_reported', fixed_sub_reported == 342, f'{fixed_sub_reported} communes reported by source'))
    results.append(check('fixed_subscription_unmatched_source', len(fixed_sub_unmatched) == 0, f'{len(fixed_sub_unmatched)} unresolved source rows'))
    results.append(check('fixed_subscription_source_not_reported', len(fixed_sub_missing) == 4, f'{len(fixed_sub_missing)} catalogue communes not reported by source'))

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

    edu = read_csv(EDU_EST)
    edu_rbd = [r['rbd'] for r in edu]
    selected = sum(r['selection_group'] == 'selected' for r in edu)
    waitlist = sum(r['selection_group'] == 'waitlist' for r in edu)
    results.append(check('education_program_records', len(edu) == 793, f'{len(edu)} program records'))
    results.append(check('education_unique_rbd', len(set(edu_rbd)) == 793, f'{len(set(edu_rbd))} unique RBD'))
    results.append(check('education_selected', selected == 700, f'{selected} selected establishments'))
    results.append(check('education_waitlist', waitlist == 93, f'{waitlist} waitlist establishments'))

    edu_communes = read_csv(EDU_COMMUNES)
    results.append(check('education_commune_rows', len(edu_communes) == 346, f'{len(edu_communes)} commune rows'))
    selected_communal = sum(int(r['mineduc_aulas_selected_establishments_2025']) for r in edu_communes)
    waitlist_communal = sum(int(r['mineduc_aulas_waitlist_establishments_2025']) for r in edu_communes)
    results.append(check('education_selected_sum_communes', selected_communal == 700, f'{selected_communal} selected summed across communes'))
    results.append(check('education_waitlist_sum_communes', waitlist_communal == 93, f'{waitlist_communal} waitlist summed across communes'))

    edu_qa = read_csv(EDU_QA)
    match_pct = qa_value(edu_qa, 'program_rbd_match_pct')
    unmatched = qa_value(edu_qa, 'program_rbd_unmatched')
    results.append(check('education_rbd_match_pct', float(match_pct or 0) == 100.0, f'match_pct={match_pct}'))
    results.append(check('education_rbd_unmatched', int(float(unmatched or -1)) == 0, f'unmatched={unmatched}'))

    html = INDEX.read_text(encoding='utf-8')
    missing_ids = sorted(dom_id for dom_id in REQUIRED_DOM_IDS if f'id="{dom_id}"' not in html)
    results.append(check('dashboard_dom_contract', not missing_ids, f'missing_ids={missing_ids}'))

    js = JS.read_text(encoding='utf-8')
    for ref in [
        'chile_digital_inclusion_communes_2026_integrated.csv',
        'chile_communes.geojson',
        'sector_snapshot_2026q1.csv',
        'mobile_5g_operators_present_2025m03',
        'mineduc_aulas_selected_establishments_2025',
        'fixed_access_public_operators_present',
        'subtel_fixed_residential_per_100_censo_households_2026m03',
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
