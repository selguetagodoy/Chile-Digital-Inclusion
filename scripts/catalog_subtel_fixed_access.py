from __future__ import annotations

import csv
from pathlib import Path
import requests

OUT = Path('data/fixed_access_infrastructure/service_catalog.csv')
FIELDS_OUT = Path('data/fixed_access_infrastructure/field_catalog.csv')

# Public ArcGIS services discovered in the SUBTEL Licancabur server.
# We deliberately keep the layer labelled RedAcceso until its contents are
# inspected; the script does not assume that every record represents fibre.
SERVICES = [
    ('CTR', 'RedAcceso', 'https://licancabur.subtel.gob.cl/server/rest/services/Of468_CTR_RedAcceso/MapServer'),
    ('Claro', 'RedAcceso', 'https://licancabur.subtel.gob.cl/server/rest/services/Of468_Claro_RedAcceso/FeatureServer'),
    ('Entel', 'RedAcceso_primarias', 'https://licancabur.subtel.gob.cl/server/rest/services/Of468_Entel_RedAcceso_primarias/FeatureServer'),
]


def get_json(url: str, params: dict | None = None):
    try:
        r = requests.get(url, params=params or {'f': 'pjson'}, timeout=60)
        r.raise_for_status()
        data = r.json()
        if isinstance(data, dict) and data.get('error'):
            return data, f"arcgis_error_{data['error'].get('code', '')}"
        return data, 'ok'
    except Exception as exc:
        return None, f'{type(exc).__name__}: {exc}'


def count(service_url: str, layer_id: int):
    data, status = get_json(
        f'{service_url}/{layer_id}/query',
        {'where': '1=1', 'returnCountOnly': 'true', 'f': 'json'},
    )
    if status == 'ok' and isinstance(data, dict) and 'count' in data:
        return int(data['count'])
    return None


def main():
    OUT.parent.mkdir(parents=True, exist_ok=True)
    rows = []
    fields = []

    for label, role, service_url in SERVICES:
        service, status = get_json(service_url)
        if status != 'ok' or not isinstance(service, dict):
            rows.append({
                'label': label, 'role': role, 'service_url': service_url,
                'status': status, 'layer_id': '', 'layer_name': '',
                'geometry_type': '', 'feature_count': '', 'capabilities': '',
                'description': '', 'copyright_text': '',
            })
            continue

        layers = service.get('layers') or []
        for layer in layers:
            layer_id = int(layer['id'])
            meta, layer_status = get_json(f'{service_url}/{layer_id}')
            meta = meta if isinstance(meta, dict) else {}
            rows.append({
                'label': label,
                'role': role,
                'service_url': service_url,
                'status': layer_status,
                'layer_id': layer_id,
                'layer_name': meta.get('name') or layer.get('name', ''),
                'geometry_type': meta.get('geometryType', ''),
                'feature_count': count(service_url, layer_id),
                'capabilities': meta.get('capabilities', service.get('capabilities', '')),
                'description': (meta.get('description') or '').replace('\n', ' ').strip(),
                'copyright_text': meta.get('copyrightText', service.get('copyrightText', '')),
            })
            for f in meta.get('fields') or []:
                fields.append({
                    'label': label,
                    'role': role,
                    'service_url': service_url,
                    'layer_id': layer_id,
                    'layer_name': meta.get('name') or layer.get('name', ''),
                    'field_name': f.get('name', ''),
                    'field_alias': f.get('alias', ''),
                    'field_type': f.get('type', ''),
                    'field_length': f.get('length', ''),
                })

    with OUT.open('w', encoding='utf-8', newline='') as fh:
        writer = csv.DictWriter(fh, fieldnames=list(rows[0].keys()) if rows else [
            'label','role','service_url','status','layer_id','layer_name','geometry_type','feature_count','capabilities','description','copyright_text'
        ])
        writer.writeheader(); writer.writerows(rows)

    with FIELDS_OUT.open('w', encoding='utf-8', newline='') as fh:
        fieldnames = ['label','role','service_url','layer_id','layer_name','field_name','field_alias','field_type','field_length']
        writer = csv.DictWriter(fh, fieldnames=fieldnames)
        writer.writeheader(); writer.writerows(fields)

    print(f'catalog rows={len(rows)} fields={len(fields)}')
    for r in rows:
        print(r['label'], r['layer_id'], r['layer_name'], r['geometry_type'], r['feature_count'])


if __name__ == '__main__':
    main()
