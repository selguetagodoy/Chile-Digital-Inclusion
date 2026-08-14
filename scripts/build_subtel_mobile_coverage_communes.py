from __future__ import annotations

import csv
import json
from collections import defaultdict
from pathlib import Path

import requests
from shapely.geometry import Point, shape
from shapely.strtree import STRtree

CATALOG = Path('data/mobile_coverage_2025/service_catalog.csv')
COMMUNE_CODES = Path('geo/commune_codes.csv')
COMMUNE_GEOJSON = Path('geo/chile_communes.geojson')
OUT_LONG = Path('data/mobile_coverage_2025/commune_operator_technology_points_2025_03.csv')
OUT_WIDE = Path('data/mobile_coverage_2025/commune_mobile_network_points_2025_03.csv')
OUT_QA = Path('data/mobile_coverage_2025/spatial_assignment_coverage.csv')


def get_json(url: str, params: dict) -> dict:
    response = requests.get(url, params=params, timeout=120)
    response.raise_for_status()
    data = response.json()
    if isinstance(data, dict) and data.get('error'):
        raise RuntimeError(f"ArcGIS error at {url}: {data['error']}")
    return data


def oid_field(service_url: str, layer_id: int) -> str:
    meta = get_json(f'{service_url}/{layer_id}', {'f': 'json'})
    field = meta.get('objectIdField') or meta.get('objectIdFieldName')
    if field:
        return field
    for item in meta.get('fields', []):
        if item.get('type') == 'esriFieldTypeOID':
            return item['name']
    raise RuntimeError(f'No ObjectID field for {service_url}/{layer_id}')


def fetch_points(service_url: str, layer_id: int) -> list[tuple[float, float]]:
    oid_name = oid_field(service_url, layer_id)
    ids_data = get_json(
        f'{service_url}/{layer_id}/query',
        {'where': '1=1', 'returnIdsOnly': 'true', 'f': 'json'},
    )
    ids = ids_data.get('objectIds') or []
    points: list[tuple[float, float]] = []

    for start in range(0, len(ids), 1000):
        chunk = ids[start:start + 1000]
        data = get_json(
            f'{service_url}/{layer_id}/query',
            {
                'objectIds': ','.join(str(v) for v in chunk),
                'outFields': oid_name,
                'returnGeometry': 'true',
                'outSR': '4326',
                'f': 'json',
            },
        )
        for feature in data.get('features', []):
            geom = feature.get('geometry') or {}
            x = geom.get('x')
            y = geom.get('y')
            if x is None or y is None:
                continue
            points.append((float(x), float(y)))
    return points


def load_communes():
    with COMMUNE_GEOJSON.open(encoding='utf-8') as fh:
        gj = json.load(fh)
    polygons = []
    props = []
    for feature in gj['features']:
        polygons.append(shape(feature['geometry']))
        props.append(feature['properties'])
    return polygons, props, STRtree(polygons)


def assign_point(lon: float, lat: float, polygons, props, tree):
    point = Point(lon, lat)
    for raw_idx in tree.query(point):
        idx = int(raw_idx)
        if polygons[idx].covers(point):
            return props[idx]
    return None


def main() -> None:
    OUT_LONG.parent.mkdir(parents=True, exist_ok=True)

    with COMMUNE_CODES.open(encoding='utf-8-sig', newline='') as fh:
        communes = list(csv.DictReader(fh))
    commune_lookup = {int(row['comuna']): row for row in communes}

    with CATALOG.open(encoding='utf-8-sig', newline='') as fh:
        catalog = [row for row in csv.DictReader(fh) if row['service_status'] == 'ok' and row['layer_id'] != '']

    polygons, props, tree = load_communes()
    counts = defaultdict(int)
    qa_rows = []

    for layer in catalog:
        operator = layer['operator']
        tech = layer['technology']
        service_url = layer['service_url']
        layer_id = int(layer['layer_id'])
        print(f'Fetching {operator} {tech}: {service_url}/{layer_id}')
        points = fetch_points(service_url, layer_id)
        assigned = 0
        for lon, lat in points:
            feature_props = assign_point(lon, lat, polygons, props, tree)
            if feature_props is None:
                continue
            code = int(feature_props['commune_code'])
            counts[(code, operator, tech)] += 1
            assigned += 1
        qa_rows.append({
            'operator': operator,
            'technology': tech,
            'period': layer['period'],
            'total_point_records': len(points),
            'assigned_to_commune': assigned,
            'unassigned': len(points) - assigned,
            'assigned_pct': round(assigned / len(points) * 100, 4) if points else '',
            'service_url': service_url,
            'layer_id': layer_id,
        })
        print(f'  points={len(points)} assigned={assigned}')

    operators = ['Claro', 'Entel', 'Movistar', 'WOM']
    technologies = ['4G', '5G']

    long_rows = []
    wide_rows = []
    for code in sorted(commune_lookup):
        c = commune_lookup[code]
        wide = {
            'comuna': code,
            'comuna_nombre': c['comuna_nombre'],
            'provincia': c['provincia'],
            'provincia_nombre': c['provincia_nombre'],
            'region': c['region'],
            'region_nombre': c['region_nombre'],
        }
        for tech in technologies:
            total = 0
            present = 0
            for operator in operators:
                value = counts[(code, operator, tech)]
                total += value
                present += int(value > 0)
                key = f"{operator.lower().replace(' ', '_')}_{tech.lower()}_point_records_2025m03"
                wide[key] = value
                long_rows.append({
                    'comuna': code,
                    'comuna_nombre': c['comuna_nombre'],
                    'region': c['region'],
                    'region_nombre': c['region_nombre'],
                    'period': '2025-03',
                    'operator': operator,
                    'technology': tech,
                    'point_records': value,
                    'interpretation': 'SUBTEL public network point records; not unique towers and not geographic coverage percentage',
                })
            wide[f'mobile_{tech.lower()}_point_records_2025m03'] = total
            wide[f'mobile_{tech.lower()}_operators_present_2025m03'] = present
        wide_rows.append(wide)

    long_fields = [
        'comuna', 'comuna_nombre', 'region', 'region_nombre', 'period',
        'operator', 'technology', 'point_records', 'interpretation',
    ]
    with OUT_LONG.open('w', encoding='utf-8', newline='') as fh:
        writer = csv.DictWriter(fh, fieldnames=long_fields)
        writer.writeheader()
        writer.writerows(long_rows)

    wide_fields = list(wide_rows[0].keys())
    with OUT_WIDE.open('w', encoding='utf-8', newline='') as fh:
        writer = csv.DictWriter(fh, fieldnames=wide_fields)
        writer.writeheader()
        writer.writerows(wide_rows)

    qa_fields = list(qa_rows[0].keys())
    with OUT_QA.open('w', encoding='utf-8', newline='') as fh:
        writer = csv.DictWriter(fh, fieldnames=qa_fields)
        writer.writeheader()
        writer.writerows(qa_rows)

    print(f'Wrote {len(long_rows)} long rows, {len(wide_rows)} commune rows and {len(qa_rows)} QA rows')


if __name__ == '__main__':
    main()
