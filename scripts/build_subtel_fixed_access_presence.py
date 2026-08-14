from __future__ import annotations

import csv
import json
import re
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

import requests

CATALOG = Path('data/fixed_access_infrastructure/service_catalog.csv')
GEO = Path('geo/chile_communes.geojson')
CODES = Path('geo/commune_codes.csv')
OUT = Path('data/fixed_access_infrastructure/commune_fixed_access_presence.csv')
QA = Path('data/fixed_access_infrastructure/presence_query_qa.csv')


def slug(label: str, role: str) -> str:
    return re.sub(r'[^a-z0-9]+', '_', f'{label}_{role}'.lower()).strip('_')


def arcgis_polygon(geometry: dict) -> dict:
    rings = []
    if geometry['type'] == 'Polygon':
        rings.extend(geometry['coordinates'])
    elif geometry['type'] == 'MultiPolygon':
        for polygon in geometry['coordinates']:
            rings.extend(polygon)
    else:
        raise ValueError(f"Unsupported geometry type {geometry['type']}")
    return {'rings': rings, 'spatialReference': {'wkid': 4326}}


def query_count(service_url: str, layer_id: int, geometry: dict) -> tuple[int | None, str]:
    try:
        r = requests.post(
            f'{service_url}/{layer_id}/query',
            data={
                'where': '1=1',
                'geometry': json.dumps(arcgis_polygon(geometry), separators=(',', ':')),
                'geometryType': 'esriGeometryPolygon',
                'inSR': '4326',
                'spatialRel': 'esriSpatialRelIntersects',
                'returnCountOnly': 'true',
                'f': 'json',
            },
            timeout=120,
        )
        r.raise_for_status()
        data = r.json()
        if data.get('error'):
            return None, f"arcgis_error_{data['error'].get('code', '')}: {data['error'].get('message', '')}"
        return int(data.get('count', 0)), 'ok'
    except Exception as exc:
        return None, f'{type(exc).__name__}: {exc}'


def main():
    OUT.parent.mkdir(parents=True, exist_ok=True)

    with CATALOG.open(encoding='utf-8-sig', newline='') as fh:
        layers = [
            r for r in csv.DictReader(fh)
            if r['status'] == 'ok' and r['layer_id'] != '' and r['geometry_type'] == 'esriGeometryPolyline'
        ]
    if not layers:
        raise RuntimeError('No accessible public RedAcceso polyline layers')

    with GEO.open(encoding='utf-8') as fh:
        gj = json.load(fh)
    geometry_by_code = {int(f['properties']['commune_code']): f['geometry'] for f in gj['features']}

    with CODES.open(encoding='utf-8-sig', newline='') as fh:
        communes = list(csv.DictReader(fh))

    counts = {}
    qa = []
    tasks = []
    with ThreadPoolExecutor(max_workers=24) as executor:
        for c in communes:
            code = int(c['comuna'])
            geom = geometry_by_code.get(code)
            if geom is None:
                for layer in layers:
                    key = slug(layer['label'], layer['role'])
                    counts[(code, key)] = 0
                    qa.append({
                        'comuna': code, 'comuna_nombre': c['comuna_nombre'],
                        'service_key': key, 'operator': layer['label'], 'network_role': layer['role'],
                        'record_count_intersecting': 0, 'status': 'no_commune_geometry',
                    })
                continue
            for layer in layers:
                key = slug(layer['label'], layer['role'])
                future = executor.submit(query_count, layer['service_url'], int(layer['layer_id']), geom)
                tasks.append((future, c, layer, key))

        for future, c, layer, key in tasks:
            count, status = future.result()
            code = int(c['comuna'])
            counts[(code, key)] = 0 if count is None else count
            qa.append({
                'comuna': code,
                'comuna_nombre': c['comuna_nombre'],
                'service_key': key,
                'operator': layer['label'],
                'network_role': layer['role'],
                'record_count_intersecting': '' if count is None else count,
                'status': status,
            })

    failed = [r for r in qa if r['status'] not in {'ok', 'no_commune_geometry'}]
    if failed:
        print('failed queries', len(failed), 'of', len(qa))
        for row in failed[:20]:
            print(row)
        raise RuntimeError(f'{len(failed)} RedAcceso spatial presence queries failed')

    service_keys = [(slug(r['label'], r['role']), r['label'], r['role']) for r in layers]
    out_rows = []
    for c in communes:
        code = int(c['comuna'])
        row = {
            'comuna': code,
            'comuna_nombre': c['comuna_nombre'],
            'provincia': c['provincia'],
            'provincia_nombre': c['provincia_nombre'],
            'region': c['region'],
            'region_nombre': c['region_nombre'],
        }
        operators = set()
        layers_present = 0
        records_sum = 0
        for key, operator, role in service_keys:
            n = int(counts.get((code, key), 0))
            row[f'{key}_records_intersecting'] = n
            records_sum += n
            if n > 0:
                layers_present += 1
                operators.add(operator)
        row['fixed_access_public_records_intersecting'] = records_sum
        row['fixed_access_public_layers_present'] = layers_present
        row['fixed_access_public_operators_present'] = len(operators)
        out_rows.append(row)

    with OUT.open('w', encoding='utf-8', newline='') as fh:
        w = csv.DictWriter(fh, fieldnames=list(out_rows[0].keys()))
        w.writeheader(); w.writerows(out_rows)
    with QA.open('w', encoding='utf-8', newline='') as fh:
        fields = ['comuna','comuna_nombre','service_key','operator','network_role','record_count_intersecting','status']
        w = csv.DictWriter(fh, fieldnames=fields); w.writeheader(); w.writerows(qa)

    print('communes', len(out_rows), 'layers', len(layers), 'queries', len(qa), 'failed', len(failed))
    print('communes with public RedAcceso layer', sum(r['fixed_access_public_layers_present'] > 0 for r in out_rows))
    print('max operators present', max(r['fixed_access_public_operators_present'] for r in out_rows))


if __name__ == '__main__':
    main()
