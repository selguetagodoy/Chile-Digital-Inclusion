from __future__ import annotations

import csv
import json
from collections import defaultdict
from pathlib import Path

import requests
from pyproj import Geod
from shapely import intersection, make_valid
from shapely.errors import GEOSException
from shapely.geometry import LineString, MultiLineString, MultiPolygon, Polygon, shape
from shapely.ops import unary_union
from shapely.strtree import STRtree

CATALOG = Path('data/fixed_access_infrastructure/service_catalog.csv')
COMMUNE_CODES = Path('geo/commune_codes.csv')
COMMUNE_GEOJSON = Path('geo/chile_communes.geojson')
OUT_LONG = Path('data/fixed_access_infrastructure/commune_operator_linework.csv')
OUT_WIDE = Path('data/fixed_access_infrastructure/commune_fixed_access_linework.csv')
OUT_QA = Path('data/fixed_access_infrastructure/spatial_assignment_coverage.csv')

GEOD = Geod(ellps='WGS84')


def get_json(url: str, params: dict) -> dict:
    r = requests.get(url, params=params, timeout=180)
    r.raise_for_status()
    data = r.json()
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


def collect_parts(geom, allowed_types: set[str]):
    if geom is None or geom.is_empty:
        return []
    if geom.geom_type in allowed_types:
        return [geom]
    if hasattr(geom, 'geoms'):
        parts = []
        for child in geom.geoms:
            parts.extend(collect_parts(child, allowed_types))
        return parts
    return []


def polygonal_only(geom):
    if geom is None or geom.is_empty:
        return None
    fixed = make_valid(geom) if not geom.is_valid else geom
    parts = collect_parts(fixed, {'Polygon', 'MultiPolygon'})
    flat = []
    for part in parts:
        if isinstance(part, Polygon):
            flat.append(part)
        elif isinstance(part, MultiPolygon):
            flat.extend(list(part.geoms))
    if not flat:
        return None
    merged = unary_union(flat)
    return merged if not merged.is_empty else None


def lineal_only(geom):
    if geom is None or geom.is_empty:
        return None
    fixed = make_valid(geom) if not geom.is_valid else geom
    parts = collect_parts(fixed, {'LineString', 'MultiLineString'})
    flat = []
    for part in parts:
        if isinstance(part, LineString):
            flat.append(part)
        elif isinstance(part, MultiLineString):
            flat.extend(list(part.geoms))
    if not flat:
        return None
    if len(flat) == 1:
        return flat[0]
    return MultiLineString(flat)


def arcgis_line(geometry: dict):
    paths = geometry.get('paths') or []
    clean = []
    for path in paths:
        coords = [(float(p[0]), float(p[1])) for p in path if len(p) >= 2]
        if len(coords) >= 2:
            clean.append(coords)
    if not clean:
        return None
    geom = LineString(clean[0]) if len(clean) == 1 else MultiLineString(clean)
    return lineal_only(geom)


def geodesic_length_m(geom) -> float:
    if geom is None or geom.is_empty:
        return 0.0
    try:
        return abs(float(GEOD.geometry_length(geom)))
    except Exception:
        if hasattr(geom, 'geoms'):
            return sum(geodesic_length_m(g) for g in geom.geoms)
        return 0.0


def safe_intersection(line, polygon):
    attempts = [
        lambda: line.intersection(polygon),
        lambda: intersection(line, polygon, grid_size=1e-8),
        lambda: intersection(lineal_only(line), polygonal_only(polygon)),
    ]
    for fn in attempts:
        try:
            out = fn()
            return lineal_only(out)
        except (GEOSException, ValueError, TypeError):
            continue
    return None


def fetch_lines(service_url: str, layer_id: int, operator: str):
    oid = oid_field(service_url, layer_id)
    ids_data = get_json(
        f'{service_url}/{layer_id}/query',
        {'where': '1=1', 'returnIdsOnly': 'true', 'f': 'json'},
    )
    ids = ids_data.get('objectIds') or []
    out_fields = [oid]
    if operator == 'Claro':
        out_fields += ['tipo_tendi', 'capacidad']
    elif operator == 'Entel':
        out_fields += ['tipo_red', 'fijacion', 'fiber_coun']

    for start in range(0, len(ids), 500):
        chunk = ids[start:start + 500]
        data = get_json(
            f'{service_url}/{layer_id}/query',
            {
                'objectIds': ','.join(str(x) for x in chunk),
                'outFields': ','.join(out_fields),
                'returnGeometry': 'true',
                'outSR': '4326',
                'f': 'json',
            },
        )
        for feature in data.get('features', []):
            geom = arcgis_line(feature.get('geometry') or {})
            if geom is not None and not geom.is_empty:
                yield feature.get('attributes') or {}, geom


def load_communes():
    with COMMUNE_GEOJSON.open(encoding='utf-8') as fh:
        gj = json.load(fh)
    polygons, props = [], []
    repaired = 0
    skipped = 0
    for f in gj['features']:
        original = shape(f['geometry'])
        geom = polygonal_only(original)
        if geom is None:
            skipped += 1
            continue
        if not original.is_valid or geom.geom_type != original.geom_type:
            repaired += 1
        polygons.append(geom)
        props.append(f['properties'])
    print('commune_geometries', len(polygons), 'repaired_or_normalized', repaired, 'skipped', skipped)
    return polygons, props, STRtree(polygons), repaired, skipped


def normalize_category(value) -> str:
    value = '' if value is None else str(value).strip()
    return value if value else 'Sin dato'


def main() -> None:
    OUT_LONG.parent.mkdir(parents=True, exist_ok=True)

    with COMMUNE_CODES.open(encoding='utf-8-sig', newline='') as fh:
        communes = list(csv.DictReader(fh))
    commune_lookup = {int(r['comuna']): r for r in communes}

    with CATALOG.open(encoding='utf-8-sig', newline='') as fh:
        layers = [
            r for r in csv.DictReader(fh)
            if r['status'] == 'ok' and r['layer_id'] != '' and r['label'] in {'Claro', 'Entel'}
        ]

    polygons, props, tree, repaired_communes, skipped_communes = load_communes()
    agg = defaultdict(lambda: {'length_m': 0.0, 'source_segments': set(), 'capacity_length_sum': 0.0,
                               'capacity_length_den': 0.0, 'fiber_count_length_sum': 0.0,
                               'fiber_count_length_den': 0.0})
    qa_rows = []

    for layer in layers:
        operator = layer['label']
        service_url = layer['service_url']
        layer_id = int(layer['layer_id'])
        total_segments = 0
        source_length_m = 0.0
        assigned_length_m = 0.0
        segments_with_assignment = 0
        overlay_failures = 0

        for attrs, line in fetch_lines(service_url, layer_id, operator):
            total_segments += 1
            source_len = geodesic_length_m(line)
            source_length_m += source_len
            matched_any = False
            oid_val = next((attrs[k] for k in attrs if k.lower() in {'objectid', 'objectid_1'}), total_segments)

            if operator == 'Claro':
                category = normalize_category(attrs.get('tipo_tendi'))
                numeric = attrs.get('capacidad')
            else:
                category = f"{normalize_category(attrs.get('tipo_red'))} | {normalize_category(attrs.get('fijacion'))}"
                numeric = attrs.get('fiber_coun')

            for raw_idx in tree.query(line):
                idx = int(raw_idx)
                try:
                    if not polygons[idx].intersects(line):
                        continue
                except GEOSException:
                    pass
                clipped = safe_intersection(line, polygons[idx])
                if clipped is None:
                    overlay_failures += 1
                    continue
                length_m = geodesic_length_m(clipped)
                if length_m <= 0:
                    continue
                code = int(props[idx]['commune_code'])
                key = (code, operator, category)
                a = agg[key]
                a['length_m'] += length_m
                a['source_segments'].add(str(oid_val))
                try:
                    num = float(numeric)
                    if operator == 'Claro':
                        a['capacity_length_sum'] += num * length_m
                        a['capacity_length_den'] += length_m
                    else:
                        a['fiber_count_length_sum'] += num * length_m
                        a['fiber_count_length_den'] += length_m
                except (TypeError, ValueError):
                    pass
                assigned_length_m += length_m
                matched_any = True
            if matched_any:
                segments_with_assignment += 1

        ratio = assigned_length_m / source_length_m * 100 if source_length_m else None
        qa_rows.append({
            'operator': operator,
            'source_segments': total_segments,
            'segments_intersecting_commune': segments_with_assignment,
            'segment_assignment_pct': round(segments_with_assignment / total_segments * 100, 4) if total_segments else '',
            'source_length_km': round(source_length_m / 1000, 3),
            'assigned_clipped_length_km': round(assigned_length_m / 1000, 3),
            'assigned_length_pct_raw': round(ratio, 4) if ratio is not None else '',
            'overlay_failures': overlay_failures,
            'commune_geometries_repaired_or_normalized': repaired_communes,
            'commune_geometries_skipped': skipped_communes,
            'service_url': service_url,
            'layer_id': layer_id,
            'interpretation': 'public RedAcceso linework split by commune intersection; tiny boundary overlaps can make summed clipped length slightly exceed source length; not household or retail coverage',
        })
        print(operator, 'segments', total_segments, 'assigned_segments', segments_with_assignment,
              'source_km', round(source_length_m/1000, 2), 'assigned_km', round(assigned_length_m/1000, 2),
              'overlay_failures', overlay_failures)

    long_rows = []
    operator_commune = defaultdict(lambda: {'length_m': 0.0, 'segments': set(), 'categories': set()})
    for (code, operator, category), a in sorted(agg.items()):
        c = commune_lookup.get(code, {})
        cap_avg = (a['capacity_length_sum'] / a['capacity_length_den']) if a['capacity_length_den'] else ''
        fiber_avg = (a['fiber_count_length_sum'] / a['fiber_count_length_den']) if a['fiber_count_length_den'] else ''
        long_rows.append({
            'comuna': code,
            'comuna_nombre': c.get('comuna_nombre', ''),
            'region': c.get('region', ''),
            'region_nombre': c.get('region_nombre', ''),
            'operator': operator,
            'network_role': 'RedAcceso' if operator == 'Claro' else 'RedAcceso_primarias',
            'category': category,
            'line_length_km': round(a['length_m'] / 1000, 4),
            'source_segments_intersecting': len(a['source_segments']),
            'length_weighted_capacity': round(cap_avg, 4) if cap_avg != '' else '',
            'length_weighted_fiber_count': round(fiber_avg, 4) if fiber_avg != '' else '',
            'interpretation': 'public regulatory linework clipped within commune; not retail service availability or coverage percentage',
        })
        oc = operator_commune[(code, operator)]
        oc['length_m'] += a['length_m']
        oc['segments'].update(a['source_segments'])
        oc['categories'].add(category)

    wide_rows = []
    for code in sorted(commune_lookup):
        c = commune_lookup[code]
        row = {
            'comuna': code,
            'comuna_nombre': c['comuna_nombre'],
            'provincia': c['provincia'],
            'provincia_nombre': c['provincia_nombre'],
            'region': c['region'],
            'region_nombre': c['region_nombre'],
        }
        present = 0
        total_km = 0.0
        for operator in ['Claro', 'Entel']:
            oc = operator_commune[(code, operator)]
            km = oc['length_m'] / 1000
            if km > 0:
                present += 1
            total_km += km
            prefix = operator.lower()
            row[f'{prefix}_redacceso_length_km'] = round(km, 4)
            row[f'{prefix}_redacceso_segments_intersecting'] = len(oc['segments'])
            row[f'{prefix}_redacceso_categories_present'] = len(oc['categories']) if km > 0 else 0
        row['fixed_access_public_linework_length_km'] = round(total_km, 4)
        row['fixed_access_public_operators_present'] = present
        wide_rows.append(row)

    with OUT_LONG.open('w', encoding='utf-8', newline='') as fh:
        fields = list(long_rows[0].keys()) if long_rows else []
        w = csv.DictWriter(fh, fieldnames=fields); w.writeheader(); w.writerows(long_rows)
    with OUT_WIDE.open('w', encoding='utf-8', newline='') as fh:
        fields = list(wide_rows[0].keys())
        w = csv.DictWriter(fh, fieldnames=fields); w.writeheader(); w.writerows(wide_rows)
    with OUT_QA.open('w', encoding='utf-8', newline='') as fh:
        fields = list(qa_rows[0].keys())
        w = csv.DictWriter(fh, fieldnames=fields); w.writeheader(); w.writerows(qa_rows)

    print('long_rows', len(long_rows), 'wide_rows', len(wide_rows))


if __name__ == '__main__':
    main()
