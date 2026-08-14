from __future__ import annotations

import csv
from pathlib import Path

import requests

OUT = Path('data/mobile_coverage_2025/service_catalog.csv')

SERVICES = [
    ('Claro', '4G', '2025-03', 'https://licancabur.subtel.gob.cl/server/rest/services/Claro_4G_marzo2025/MapServer'),
    ('Claro', '5G', '2025-03', 'https://licancabur.subtel.gob.cl/server/rest/services/Claro_5G_marzo2025/FeatureServer'),
    ('Entel', '4G', '2025-03', 'https://licancabur.subtel.gob.cl/server/rest/services/Entel_4G_marzo2025/FeatureServer'),
    ('Entel', '5G', '2025-03', 'https://licancabur.subtel.gob.cl/server/rest/services/Entel_5G_marzo2025/FeatureServer'),
    ('Movistar', '4G', '2025-03', 'https://licancabur.subtel.gob.cl/server/rest/services/Movistar_4G_marzo2025/MapServer'),
    ('Movistar', '5G', '2025-03', 'https://licancabur.subtel.gob.cl/server/rest/services/Movistar_5G_marzo2025/MapServer'),
    ('WOM', '4G', '2025-03', 'https://licancabur.subtel.gob.cl/server/rest/services/Wom_4G_marzo2025/FeatureServer'),
    ('WOM', '5G', '2025-03', 'https://licancabur.subtel.gob.cl/server/rest/services/Wom_5G_marzo2025/MapServer'),
]


def get_json(url: str, params: dict | None = None) -> tuple[dict | None, str]:
    try:
        r = requests.get(url, params=params or {'f': 'pjson'}, timeout=60)
        r.raise_for_status()
        data = r.json()
        if isinstance(data, dict) and data.get('error'):
            return data, f"arcgis_error_{data['error'].get('code', '')}"
        return data, 'ok'
    except Exception as exc:
        return None, f'{type(exc).__name__}: {exc}'


def layer_count(service_url: str, layer_id: int) -> int | None:
    data, status = get_json(
        f'{service_url}/{layer_id}/query',
        {'where': '1=1', 'returnCountOnly': 'true', 'f': 'json'},
    )
    if status == 'ok' and isinstance(data, dict):
        try:
            return int(data['count'])
        except Exception:
            return None
    return None


def main() -> None:
    OUT.parent.mkdir(parents=True, exist_ok=True)
    rows: list[dict] = []

    for operator, technology, period, service_url in SERVICES:
        service, status = get_json(service_url)
        if status != 'ok' or not isinstance(service, dict):
            rows.append({
                'operator': operator,
                'technology': technology,
                'period': period,
                'service_url': service_url,
                'service_status': status,
                'service_name': '',
                'service_type': '',
                'layer_id': '',
                'layer_name': '',
                'geometry_type': '',
                'feature_count': '',
                'max_record_count': '',
                'capabilities': '',
                'copyright_text': '',
            })
            continue

        layers = service.get('layers') or []
        if not layers:
            rows.append({
                'operator': operator,
                'technology': technology,
                'period': period,
                'service_url': service_url,
                'service_status': 'ok_no_layers',
                'service_name': service.get('mapName') or service.get('name') or '',
                'service_type': service.get('type') or '',
                'layer_id': '',
                'layer_name': '',
                'geometry_type': '',
                'feature_count': '',
                'max_record_count': service.get('maxRecordCount', ''),
                'capabilities': service.get('capabilities', ''),
                'copyright_text': service.get('copyrightText', ''),
            })
            continue

        for layer in layers:
            layer_id = int(layer['id'])
            meta, layer_status = get_json(f'{service_url}/{layer_id}')
            meta = meta if isinstance(meta, dict) else {}
            rows.append({
                'operator': operator,
                'technology': technology,
                'period': period,
                'service_url': service_url,
                'service_status': layer_status,
                'service_name': service.get('mapName') or service.get('name') or '',
                'service_type': service.get('type') or '',
                'layer_id': layer_id,
                'layer_name': meta.get('name') or layer.get('name', ''),
                'geometry_type': meta.get('geometryType', ''),
                'feature_count': layer_count(service_url, layer_id),
                'max_record_count': meta.get('maxRecordCount', service.get('maxRecordCount', '')),
                'capabilities': meta.get('capabilities', service.get('capabilities', '')),
                'copyright_text': meta.get('copyrightText', service.get('copyrightText', '')),
            })

    fields = [
        'operator', 'technology', 'period', 'service_url', 'service_status',
        'service_name', 'service_type', 'layer_id', 'layer_name', 'geometry_type',
        'feature_count', 'max_record_count', 'capabilities', 'copyright_text',
    ]
    with OUT.open('w', encoding='utf-8', newline='') as fh:
        writer = csv.DictWriter(fh, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)

    print(f'Wrote {len(rows)} rows to {OUT}')
    for row in rows:
        print(row['operator'], row['technology'], row['service_status'], row['layer_id'], row['layer_name'], row['feature_count'])


if __name__ == '__main__':
    main()
