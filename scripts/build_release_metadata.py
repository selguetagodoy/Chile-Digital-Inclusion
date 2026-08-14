#!/usr/bin/env python3
"""Build public layer catalog and file-level release manifest.

The catalog is explicit: it documents the analytical contract of the repository.
The manifest is generated from committed public files and records basic structural
metadata plus a SHA-256 checksum for reproducibility.
"""

from __future__ import annotations

import csv
import hashlib
from pathlib import Path

ROOT = Path('.')
META = ROOT / 'data/metadata'
LAYER_OUT = META / 'layer_catalog.csv'
MANIFEST_OUT = META / 'release_manifest.csv'

LAYERS = [
    {
        'layer_id': 'communal_master_2026',
        'path': 'data/communal_master/chile_digital_inclusion_communes_2026_integrated.csv',
        'source_family': 'Integrated public layer',
        'reference_period': '2024-2026',
        'territorial_level': 'commune',
        'statistical_unit': 'mixed; see variable dictionary',
        'role': 'canonical integrated communal analytical table',
        'canonical': 'yes',
        'license_note': 'Mixed-source derivative; source-specific terms apply',
    },
    {
        'layer_id': 'censo_connectivity_2024',
        'path': 'data/censo_2024/communes_connectivity_2024.csv',
        'source_family': 'INE / Censo 2024',
        'reference_period': '2024',
        'territorial_level': 'commune',
        'statistical_unit': 'household',
        'role': 'structural household connectivity and equipment',
        'canonical': 'yes',
        'license_note': 'Public source; retain source attribution',
    },
    {
        'layer_id': 'censo_social_context_2024',
        'path': 'data/censo_2024/communes_social_context_2024.csv',
        'source_family': 'INE / Censo 2024',
        'reference_period': '2024',
        'territorial_level': 'commune',
        'statistical_unit': 'household',
        'role': 'communal household and social context',
        'canonical': 'yes',
        'license_note': 'Public source; retain source attribution',
    },
    {
        'layer_id': 'casen_national_2024',
        'path': 'data/casen_national_2024.csv',
        'source_family': 'MDSF / CASEN 2024',
        'reference_period': '2024',
        'territorial_level': 'national',
        'statistical_unit': 'weighted person',
        'role': 'national access and social-gap benchmark',
        'canonical': 'yes',
        'license_note': 'Derived aggregate from public survey; retain source attribution',
    },
    {
        'layer_id': 'casen_macrozone_2024',
        'path': 'data/casen_macrozones_2024.csv',
        'source_family': 'MDSF / CASEN 2024',
        'reference_period': '2024',
        'territorial_level': 'macrozone',
        'statistical_unit': 'weighted person',
        'role': 'macro-territorial social and connectivity comparison',
        'canonical': 'yes',
        'license_note': 'Derived aggregate from public survey; retain source attribution',
    },
    {
        'layer_id': 'subtel_longitudinal_access',
        'path': 'data/subtel_longitudinal/subtel_household_digital_access_2015_2025.csv',
        'source_family': 'SUBTEL access/use surveys',
        'reference_period': '2015-2025',
        'territorial_level': 'national / urban-rural',
        'statistical_unit': 'household',
        'role': 'harmonized household access series',
        'canonical': 'yes',
        'license_note': 'Derived aggregate from official public survey waves',
    },
    {
        'layer_id': 'subtel_microdata_inventory',
        'path': 'data/subtel_microdata/processed_base_catalog.csv',
        'source_family': 'SUBTEL access/use survey SAV files',
        'reference_period': '2008-2025',
        'territorial_level': 'survey metadata',
        'statistical_unit': 'base/questionnaire metadata',
        'role': 'processed-wave and weighting audit catalog',
        'canonical': 'yes',
        'license_note': 'Metadata/aggregates only; original microdata are not republished',
    },
    {
        'layer_id': 'subtel_segmented_access',
        'path': 'data/subtel_segments/household_paid_access_by_segment_2015_2025.csv',
        'source_family': 'SUBTEL access/use survey SAV files',
        'reference_period': '2015-2025 comparable waves',
        'territorial_level': 'national / region / urban-rural / verified SES',
        'statistical_unit': 'weighted household',
        'role': 'segmented household access estimates',
        'canonical': 'yes',
        'license_note': 'Derived aggregate; small cells suppressed where applicable',
    },
    {
        'layer_id': 'subtel_affordability',
        'path': 'data/affordability/subtel_willingness_to_pay_2023_2025.csv',
        'source_family': 'SUBTEL access/use surveys',
        'reference_period': '2023-2025',
        'territorial_level': 'national',
        'statistical_unit': 'weighted household / respondent universe',
        'role': 'declared willingness to pay; not market price',
        'canonical': 'yes',
        'license_note': 'Derived aggregate from official public survey waves',
    },
    {
        'layer_id': 'subtel_sector_2026q1',
        'path': 'data/subtel_sector_2026/sector_snapshot_2026q1.csv',
        'source_family': 'SUBTEL sector statistics',
        'reference_period': '2026Q1',
        'territorial_level': 'national',
        'statistical_unit': 'connection / sector estimate',
        'role': 'current sector context and technology mix',
        'canonical': 'yes',
        'license_note': 'Public official statistics; retain source attribution',
    },
    {
        'layer_id': 'subtel_sector_longitudinal_2026m03',
        'path': 'data/subtel_sector_series/sector_core_monthly_long.csv',
        'source_family': 'SUBTEL administrative Internet series',
        'reference_period': 'effective workbook ranges through 2026-03',
        'territorial_level': 'national monthly',
        'statistical_unit': 'connection / traffic aggregate',
        'role': 'canonical longitudinal fixed/mobile connection and traffic series',
        'canonical': 'yes',
        'license_note': 'Public official XLSX sources; provenance discrepancies are retained rather than force-reconciled',
    },
    {
        'layer_id': 'subtel_oti_fixed_speed_2026m01',
        'path': 'data/oti_2026/regional_fixed_speed_2026_01.csv',
        'source_family': 'SUBTEL / Organismo Técnico Independiente',
        'reference_period': '2026-01',
        'territorial_level': 'region',
        'statistical_unit': 'OTI fixed Internet measurement aggregate',
        'role': 'official regional fixed-speed benchmark kept separate from Ookla',
        'canonical': 'yes',
        'license_note': 'Public official publication; measurement system and universe differ from Ookla and household access statistics',
    },
    {
        'layer_id': 'subtel_mobile_network_2025m03',
        'path': 'data/mobile_coverage_2025/commune_mobile_network_points_2025_03.csv',
        'source_family': 'SUBTEL ArcGIS 4G/5G',
        'reference_period': '2025-03',
        'territorial_level': 'commune',
        'statistical_unit': 'published network point record',
        'role': 'observable public mobile-network records by operator and technology',
        'canonical': 'yes',
        'license_note': 'Public regulatory records; counts are not unique towers or coverage rates',
    },
    {
        'layer_id': 'subtel_fixed_redacceso_presence',
        'path': 'data/fixed_access_infrastructure/commune_fixed_access_presence.csv',
        'source_family': 'SUBTEL ArcGIS RedAcceso',
        'reference_period': 'public service snapshot 2026-08',
        'territorial_level': 'commune',
        'statistical_unit': 'public linework layer / operator presence',
        'role': 'public fixed-access linework presence by commune',
        'canonical': 'yes',
        'license_note': 'Regulatory linework presence; not retail availability or household coverage',
    },
    {
        'layer_id': 'subtel_fixed_redacceso_length_audit',
        'path': 'data/fixed_access_infrastructure/commune_fixed_access_linework.csv',
        'source_family': 'SUBTEL ArcGIS RedAcceso',
        'reference_period': 'public service snapshot 2026-08',
        'territorial_level': 'commune',
        'statistical_unit': 'clipped line segment',
        'role': 'technical geodesic linework audit; not master dependency',
        'canonical': 'no',
        'license_note': 'Technical derivative; overlapping layers and boundary effects must be considered',
    },
    {
        'layer_id': 'mineduc_aulas_establishments_2025',
        'path': 'data/education_connectivity_2026/aulas_conectadas_2025_establishments_enriched.csv',
        'source_family': 'Mineduc Aulas Conectadas + Official Establishment Directory',
        'reference_period': '2025',
        'territorial_level': 'establishment',
        'statistical_unit': 'RBD establishment',
        'role': 'selected and waitlist establishments enriched with official territory',
        'canonical': 'yes',
        'license_note': 'Public administrative records; unnecessary personal/admin identifiers excluded',
    },
    {
        'layer_id': 'mineduc_aulas_communal_2025',
        'path': 'data/education_connectivity_2026/aulas_conectadas_2025_commune_summary.csv',
        'source_family': 'Mineduc Aulas Conectadas + Official Establishment Directory',
        'reference_period': '2025',
        'territorial_level': 'commune',
        'statistical_unit': 'RBD establishment aggregate',
        'role': 'communal education-connectivity program context',
        'canonical': 'yes',
        'license_note': 'Program selection is not installed connectivity or household access',
    },
    {
        'layer_id': 'ookla_national_2026q1',
        'path': 'data/ookla/chile_2026q1_summary.csv',
        'source_family': 'Ookla Open Data',
        'reference_period': '2026Q1',
        'territorial_level': 'national',
        'statistical_unit': 'Speedtest tile/test aggregate',
        'role': 'observed fixed and mobile network performance',
        'canonical': 'yes',
        'license_note': 'CC BY-NC-SA 4.0 source terms apply to derived Ookla data',
    },
    {
        'layer_id': 'ookla_communal_2026q1',
        'path': 'data/ookla/territorial/chile_2026q1_communes.csv',
        'source_family': 'Ookla Open Data',
        'reference_period': '2026Q1',
        'territorial_level': 'commune × network',
        'statistical_unit': 'Speedtest tile/test aggregate',
        'role': 'communal observed network performance',
        'canonical': 'yes',
        'license_note': 'CC BY-NC-SA 4.0 source terms apply to derived Ookla data',
    },
    {
        'layer_id': 'commune_geography',
        'path': 'geo/chile_communes.geojson',
        'source_family': 'Biblioteca del Congreso Nacional',
        'reference_period': 'current public layer used in release',
        'territorial_level': 'commune',
        'statistical_unit': 'polygon',
        'role': 'map geometry and spatial joins',
        'canonical': 'yes',
        'license_note': 'Public source; retain attribution and geometry coverage caveat',
    },
]

MANIFEST_DIRS = [Path('data'), Path('geo'), Path('docs'), Path('scripts')]
MANIFEST_FILES = [Path('README.md'), Path('CITATION.cff'), Path('index.html'), Path('assets/dashboard.js'), Path('assets/dashboard.css')]
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
    if suffix == '.csv': return 'csv'
    if suffix in {'.md', '.cff', '.html', '.js', '.css', '.py', '.yml', '.yaml'}: return suffix.lstrip('.')
    if suffix in {'.json', '.geojson'}: return suffix.lstrip('.')
    return suffix.lstrip('.') or 'file'


def main() -> None:
    META.mkdir(parents=True, exist_ok=True)

    layer_fields = ['layer_id','path','source_family','reference_period','territorial_level','statistical_unit','role','canonical','license_note','exists','rows','columns']
    layer_rows = []
    for layer in LAYERS:
        row = dict(layer)
        path = ROOT / layer['path']
        row['exists'] = 'yes' if path.exists() else 'no'
        if path.exists() and path.suffix.lower() == '.csv':
            rows, cols = csv_shape(path)
        else:
            rows, cols = '', ''
        row['rows'], row['columns'] = rows, cols
        layer_rows.append(row)

    with LAYER_OUT.open('w', encoding='utf-8', newline='') as fh:
        w = csv.DictWriter(fh, fieldnames=layer_fields)
        w.writeheader(); w.writerows(layer_rows)

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
        fields = ['path','file_type','bytes','rows','columns','sha256']
        w = csv.DictWriter(fh, fieldnames=fields)
        w.writeheader(); w.writerows(manifest_rows)

    missing_canonical = [r['layer_id'] for r in layer_rows if r['canonical'] == 'yes' and r['exists'] != 'yes']
    if missing_canonical:
        raise RuntimeError(f'Missing canonical layers: {missing_canonical}')

    print('layer_catalog_rows', len(layer_rows))
    print('release_manifest_files', len(manifest_rows))
    print('canonical_layers', sum(r['canonical'] == 'yes' for r in layer_rows))
    print('optional_layers', sum(r['canonical'] == 'no' for r in layer_rows))


if __name__ == '__main__':
    main()
