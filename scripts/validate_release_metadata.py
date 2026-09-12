#!/usr/bin/env python3
"""Validate the machine-readable release metadata contract."""

from __future__ import annotations

import csv
from pathlib import Path

CATALOG = Path('data/metadata/layer_catalog.csv')
MANIFEST = Path('data/metadata/release_manifest.csv')
REPRO = Path('docs/reproducibility.md')

REQUIRED_CANONICAL = {
    'communal_master_2026',
    'censo_connectivity_2024',
    'censo_social_context_2024',
    'casen_national_2024',
    'casen_macrozone_2024',
    'subtel_longitudinal_access',
    'subtel_microdata_inventory',
    'subtel_segmented_access',
    'subtel_affordability',
    'subtel_sector_2026q2',
    'subtel_portability_2026q2',
    'subtel_fdt_projects_2026q1',
    'subtel_fdt_project_updates_2026',
    'subtel_network_resilience_2026',
    'subtel_sector_longitudinal_2026m06',
    'subtel_oti_fixed_speed_2026m01',
    'subtel_mobile_network_2025m03',
    'subtel_fixed_connections_communal_2026m06',
    'subtel_fixed_redacceso_presence',
    'mineduc_aulas_establishments_2025',
    'mineduc_aulas_communal_2025',
    'ookla_national_2026q1',
    'ookla_communal_2026q1',
    'commune_geography',
}

EXPECTED_NONCANONICAL = {
    'subtel_fixed_redacceso_length_audit',
    'subtel_fdt_spectrum_obligations_2026q1',
}

REQUIRED_MANIFEST_PATHS = {
    'README.md',
    'CITATION.cff',
    'index.html',
    'assets/dashboard.js',
    'data/communal_master/chile_digital_inclusion_communes_2026_integrated.csv',
    'data/fixed_infrastructure_2026/commune_fixed_connections_2026_06.csv',
    'data/fixed_infrastructure_2026/source_alignment_qa_2026_06.csv',
    'data/fixed_infrastructure_2026/source_row_mapping_2026_06.csv',
    'data/metadata/public_release_validation.csv',
    'data/oti_2026/regional_fixed_speed_2026_01.csv',
    'data/fdt_2026/fdt_projects_q1_2026.csv',
    'data/fdt_2026/fdt_project_updates_2026.csv',
    'data/fdt_2026/spectrum_obligations_q1_2026.csv',
    'data/network_resilience_2026/network_resilience_observations_2026.csv',
    'docs/fdt_2026.md',
    'docs/network_resilience_2026.md',
    'docs/reproducibility.md',
    'docs/communal_master_dictionary.md',
    'geo/chile_communes.geojson',
}


def read_csv(path: Path):
    with path.open(encoding='utf-8-sig', newline='') as fh:
        return list(csv.DictReader(fh))


def require_shape(catalog, layer_id: str, rows: int, columns: int | None = None) -> None:
    item = next(r for r in catalog if r['layer_id'] == layer_id)
    if int(item['rows']) != rows:
        raise RuntimeError(f'{layer_id} row mismatch: {item["rows"]} != {rows}')
    if columns is not None and int(item['columns']) != columns:
        raise RuntimeError(f'{layer_id} column mismatch: {item["columns"]} != {columns}')


def main() -> None:
    for path in [CATALOG, MANIFEST, REPRO]:
        if not path.exists():
            raise RuntimeError(f'Missing release metadata file: {path}')

    catalog = read_csv(CATALOG)
    ids = [r['layer_id'] for r in catalog]
    if len(ids) != len(set(ids)):
        raise RuntimeError('Duplicate layer_id in layer catalog')

    expected_ids = REQUIRED_CANONICAL | EXPECTED_NONCANONICAL
    actual_ids = set(ids)
    if actual_ids != expected_ids:
        raise RuntimeError(
            'Layer catalog contract changed. '
            f'Missing={sorted(expected_ids-actual_ids)} Extra={sorted(actual_ids-expected_ids)}'
        )

    canonical = {r['layer_id'] for r in catalog if r['canonical'] == 'yes'}
    if canonical != REQUIRED_CANONICAL:
        raise RuntimeError(
            'Canonical layer contract changed. '
            f'Missing={sorted(REQUIRED_CANONICAL-canonical)} Extra={sorted(canonical-REQUIRED_CANONICAL)}'
        )

    unavailable = [r['layer_id'] for r in catalog if r['canonical'] == 'yes' and r['exists'] != 'yes']
    if unavailable:
        raise RuntimeError(f'Canonical catalog layers unavailable: {unavailable}')

    require_shape(catalog, 'communal_master_2026', 346, 94)
    require_shape(catalog, 'subtel_sector_2026q2', 60, 9)
    require_shape(catalog, 'subtel_portability_2026q2', 10, 10)
    require_shape(catalog, 'subtel_sector_longitudinal_2026m06', 2020, 9)
    require_shape(catalog, 'subtel_fixed_connections_communal_2026m06', 346, 13)
    require_shape(catalog, 'subtel_oti_fixed_speed_2026m01', 16, 9)
    require_shape(catalog, 'subtel_fdt_projects_2026q1', 14, 12)
    require_shape(catalog, 'subtel_fdt_project_updates_2026', 2, 20)
    require_shape(catalog, 'subtel_fdt_spectrum_obligations_2026q1', 3, 11)
    require_shape(catalog, 'subtel_network_resilience_2026', 18, 14)

    manifest = read_csv(MANIFEST)
    if len(manifest) < 180:
        raise RuntimeError(f'Release manifest unexpectedly small: {len(manifest)} files')
    paths = [r['path'] for r in manifest]
    if len(paths) != len(set(paths)):
        raise RuntimeError('Duplicate path in release manifest')
    path_set = set(paths)
    missing = REQUIRED_MANIFEST_PATHS - path_set
    if missing:
        raise RuntimeError(f'Manifest missing required public files: {sorted(missing)}')
    if 'data/metadata/release_manifest.csv' in path_set or 'data/metadata/layer_catalog.csv' in path_set:
        raise RuntimeError('Autogenerated release metadata must not hash itself')

    bad_hashes = [r['path'] for r in manifest if len(r.get('sha256', '')) != 64]
    if bad_hashes:
        raise RuntimeError(f'Invalid SHA-256 entries: {bad_hashes[:10]}')

    print('release_metadata PASS')
    print('layers', len(catalog), 'canonical', len(canonical), 'manifest_files', len(manifest))


if __name__ == '__main__':
    main()
