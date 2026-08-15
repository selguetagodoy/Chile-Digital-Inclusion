#!/usr/bin/env python3
"""Build public layer catalog and file-level release manifest.

The layer catalog is an explicit analytical contract. The manifest inventories
committed public files with basic structural metadata and SHA-256 checksums.
"""

from __future__ import annotations

import csv
import hashlib
from pathlib import Path

ROOT = Path('.')
META = ROOT / 'data/metadata'
LAYER_OUT = META / 'layer_catalog.csv'
MANIFEST_OUT = META / 'release_manifest.csv'


def layer(layer_id, path, source_family, reference_period, territorial_level,
          statistical_unit, role, canonical='yes', license_note='Public source; retain source attribution'):
    return {
        'layer_id': layer_id,
        'path': path,
        'source_family': source_family,
        'reference_period': reference_period,
        'territorial_level': territorial_level,
        'statistical_unit': statistical_unit,
        'role': role,
        'canonical': canonical,
        'license_note': license_note,
    }


LAYERS = [
    layer(
        'communal_master_2026',
        'data/communal_master/chile_digital_inclusion_communes_2026_integrated.csv',
        'Integrated public layer', '2024-2026', 'commune',
        'mixed; see variable dictionary', 'canonical integrated communal analytical table',
        license_note='Mixed-source derivative; source-specific terms apply',
    ),
    layer(
        'censo_connectivity_2024', 'data/censo_2024/communes_connectivity_2024.csv',
        'INE / Censo 2024', '2024', 'commune', 'household',
        'structural household connectivity and equipment',
    ),
    layer(
        'censo_social_context_2024', 'data/censo_2024/communes_social_context_2024.csv',
        'INE / Censo 2024', '2024', 'commune', 'household',
        'communal household and social context',
    ),
    layer(
        'casen_national_2024', 'data/casen_national_2024.csv', 'MDSF / CASEN 2024',
        '2024', 'national', 'weighted person', 'national access and social-gap benchmark',
        license_note='Derived aggregate from public survey; retain source attribution',
    ),
    layer(
        'casen_macrozone_2024', 'data/casen_macrozones_2024.csv', 'MDSF / CASEN 2024',
        '2024', 'macrozone', 'weighted person', 'macro-territorial social and connectivity comparison',
        license_note='Derived aggregate from public survey; retain source attribution',
    ),
    layer(
        'subtel_longitudinal_access',
        'data/subtel_longitudinal/subtel_household_digital_access_2015_2025.csv',
        'SUBTEL access/use surveys', '2015-2025', 'national / urban-rural', 'household',
        'harmonized household access series',
        license_note='Derived aggregate from official public survey waves',
    ),
    layer(
        'subtel_microdata_inventory', 'data/subtel_microdata/processed_base_catalog.csv',
        'SUBTEL access/use survey SAV files', '2008-2025', 'survey metadata',
        'base/questionnaire metadata', 'processed-wave and weighting audit catalog',
        license_note='Metadata/aggregates only; original microdata are not republished',
    ),
    layer(
        'subtel_segmented_access',
        'data/subtel_segments/household_paid_access_by_segment_2015_2025.csv',
        'SUBTEL access/use survey SAV files', '2015-2025 comparable waves',
        'national / region / urban-rural / verified SES', 'weighted household',
        'segmented household access estimates',
        license_note='Derived aggregate; small cells suppressed where applicable',
    ),
    layer(
        'subtel_affordability', 'data/affordability/subtel_willingness_to_pay_2023_2025.csv',
        'SUBTEL access/use surveys', '2023-2025', 'national',
        'weighted household / respondent universe', 'declared willingness to pay; not market price',
        license_note='Derived aggregate from official public survey waves',
    ),
    layer(
        'subtel_sector_2026q1', 'data/subtel_sector_2026/sector_snapshot_2026q1.csv',
        'SUBTEL sector statistics', '2026Q1', 'national', 'connection / sector estimate',
        'current sector context and technology mix',
    ),
    layer(
        'subtel_sector_longitudinal_2026m03', 'data/subtel_sector_series/sector_core_monthly_long.csv',
        'SUBTEL administrative Internet series', 'effective workbook ranges through 2026-03',
        'national monthly', 'connection / traffic aggregate',
        'canonical longitudinal fixed/mobile connection and traffic series',
        license_note='Public official XLSX sources; provenance discrepancies are retained rather than force-reconciled',
    ),
    layer(
        'subtel_oti_fixed_speed_2026m01', 'data/oti_2026/regional_fixed_speed_2026_01.csv',
        'SUBTEL / Organismo Técnico Independiente', '2026-01', 'region',
        'OTI fixed Internet measurement aggregate',
        'official regional fixed-speed benchmark kept separate from Ookla',
        license_note='Public official publication; measurement system and universe differ from Ookla and household access statistics',
    ),
    layer(
        'subtel_mobile_network_2025m03',
        'data/mobile_coverage_2025/commune_mobile_network_points_2025_03.csv',
        'SUBTEL ArcGIS 4G/5G', '2025-03', 'commune', 'published network point record',
        'observable public mobile-network records by operator and technology',
        license_note='Public regulatory records; counts are not unique towers or coverage rates',
    ),
    layer(
        'subtel_fixed_connections_communal_2026m03',
        'data/fixed_infrastructure_2026/commune_fixed_connections_2026_03.csv',
        'SUBTEL administrative fixed Internet workbook', '2026-03', 'commune',
        'administrative fixed connection',
        'reconciled communal total and residential fixed Internet connections',
        license_note='Public official XLSX source; reconstructed from formula-defined regional blocks. Antártica (12202) is an explicit source blank, not an imputed zero',
    ),
    layer(
        'subtel_fixed_redacceso_presence',
        'data/fixed_access_infrastructure/commune_fixed_access_presence.csv',
        'SUBTEL ArcGIS RedAcceso', 'public service snapshot 2026-08', 'commune',
        'public linework layer / operator presence', 'public fixed-access linework presence by commune',
        license_note='Regulatory linework presence; not retail availability or household coverage',
    ),
    layer(
        'subtel_fixed_redacceso_length_audit',
        'data/fixed_access_infrastructure/commune_fixed_access_linework.csv',
        'SUBTEL ArcGIS RedAcceso', 'public service snapshot 2026-08', 'commune',
        'clipped line segment', 'technical geodesic linework audit; not master dependency',
        canonical='no',
        license_note='Technical derivative; overlapping layers and boundary effects must be considered',
    ),
    layer(
        'mineduc_aulas_establishments_2025',
        'data/education_connectivity_2026/aulas_conectadas_2025_establishments_enriched.csv',
        'Mineduc Aulas Conectadas + Official Establishment Directory', '2025', 'establishment',
        'RBD establishment', 'selected and waitlist establishments enriched with official territory',
        license_note='Public administrative records; unnecessary personal/admin identifiers excluded',
    ),
    layer(
        'mineduc_aulas_communal_2025',
        'data/education_connectivity_2026/aulas_conectadas_2025_commune_summary.csv',
        'Mineduc Aulas Conectadas + Official Establishment Directory', '2025', 'commune',
        'RBD establishment aggregate', 'communal education-connectivity program context',
        license_note='Program selection is not installed connectivity or household access',
    ),
    layer(
        'ookla_national_2026q1', 'data/ookla/chile_2026q1_summary.csv', 'Ookla Open Data',
        '2026Q1', 'national', 'Speedtest tile/test aggregate',
        'observed fixed and mobile network performance',
        license_note='CC BY-NC-SA 4.0 source terms apply to derived Ookla data',
    ),
    layer(
        'ookla_communal_2026q1', 'data/ookla/territorial/chile_2026q1_communes.csv',
        'Ookla Open Data', '2026Q1', 'commune × network', 'Speedtest tile/test aggregate',
        'communal observed network performance',
        license_note='CC BY-NC-SA 4.0 source terms apply to derived Ookla data',
    ),
    layer(
        'commune_geography', 'geo/chile_communes.geojson', 'Biblioteca del Congreso Nacional',
        'current public layer used in release', 'commune', 'polygon',
        'map geometry and spatial joins',
        license_note='Public source; retain attribution and geometry coverage caveat',
    ),
]

MANIFEST_DIRS = [Path('data'), Path('geo'), Path('docs'), Path('scripts')]
MANIFEST_FILES = [
    Path('README.md'), Path('CITATION.cff'), Path('index.html'),
    Path('assets/dashboard.js'), Path('assets/dashboard.css'),
]
AUTOGENERATED_METADATA = {LAYER_OUT, MANIFEST_OUT}


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open('rb') as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()


def csv_shape(path: Path):
    try:
        with path.open(encoding='utf-8-sig', newline='') as fh:
            reader = csv.reader(fh)
            header = next(reader, [])
            rows = sum(1 for _ in reader)
        return rows, len(header)
    except (UnicodeDecodeError, csv.Error):
        return '', ''


def file_kind(path: Path) -> str:
    suffix = path.suffix.lower()
    if suffix == '.csv':
        return 'csv'
    if suffix in {'.md', '.cff', '.html', '.js', '.css', '.py', '.yml', '.yaml'}:
        return suffix.lstrip('.')
    if suffix in {'.json', '.geojson'}:
        return suffix.lstrip('.')
    return suffix.lstrip('.') or 'file'


def main() -> None:
    META.mkdir(parents=True, exist_ok=True)

    layer_fields = [
        'layer_id', 'path', 'source_family', 'reference_period', 'territorial_level',
        'statistical_unit', 'role', 'canonical', 'license_note', 'exists', 'rows', 'columns',
    ]
    layer_rows = []
    for item in LAYERS:
        row = dict(item)
        path = ROOT / item['path']
        row['exists'] = 'yes' if path.exists() else 'no'
        if path.exists() and path.suffix.lower() == '.csv':
            rows, cols = csv_shape(path)
        else:
            rows, cols = '', ''
        row['rows'], row['columns'] = rows, cols
        layer_rows.append(row)

    with LAYER_OUT.open('w', encoding='utf-8', newline='') as fh:
        writer = csv.DictWriter(fh, fieldnames=layer_fields)
        writer.writeheader()
        writer.writerows(layer_rows)

    paths = set(MANIFEST_FILES)
    for directory in MANIFEST_DIRS:
        if directory.exists():
            paths.update(p for p in directory.rglob('*') if p.is_file())
    paths = {
        p for p in paths
        if '__pycache__' not in p.parts
        and '.git' not in p.parts
        and p not in AUTOGENERATED_METADATA
    }

    manifest_rows = []
    for path in sorted(paths, key=lambda p: p.as_posix()):
        kind = file_kind(path)
        rows = cols = ''
        if kind == 'csv':
            rows, cols = csv_shape(path)
        manifest_rows.append({
            'path': path.as_posix(),
            'file_type': kind,
            'bytes': path.stat().st_size,
            'rows': rows,
            'columns': cols,
            'sha256': sha256(path),
        })

    with MANIFEST_OUT.open('w', encoding='utf-8', newline='') as fh:
        fields = ['path', 'file_type', 'bytes', 'rows', 'columns', 'sha256']
        writer = csv.DictWriter(fh, fieldnames=fields)
        writer.writeheader()
        writer.writerows(manifest_rows)

    missing_canonical = [
        row['layer_id'] for row in layer_rows
        if row['canonical'] == 'yes' and row['exists'] != 'yes'
    ]
    if missing_canonical:
        raise RuntimeError(f'Missing canonical layers: {missing_canonical}')

    print('layer_catalog_rows', len(layer_rows))
    print('release_manifest_files', len(manifest_rows))
    print('canonical_layers', sum(row['canonical'] == 'yes' for row in layer_rows))
    print('optional_layers', sum(row['canonical'] == 'no' for row in layer_rows))


if __name__ == '__main__':
    main()
