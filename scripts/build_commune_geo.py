#!/usr/bin/env python3
"""Build a lightweight Chile commune GeoJSON from the BCN communal boundary service."""

from __future__ import annotations

import json
from pathlib import Path

import requests

ENDPOINT = "https://arcgiswebad.bcn.cl/arcgis/rest/services/Hosted/Capa_Factores/FeatureServer/0/query"
OUT = Path("geo/chile_communes.geojson")


def main() -> None:
    params = {
        "where": "1=1",
        "outFields": "cod_comuna,nom_com,nom_prov,nom_reg,codregion",
        "returnGeometry": "true",
        "outSR": "4326",
        "geometryPrecision": "5",
        "maxAllowableOffset": "0.001",
        "f": "geojson",
    }
    response = requests.get(ENDPOINT, params=params, timeout=180)
    response.raise_for_status()
    data = response.json()
    features = data.get("features", [])
    if len(features) < 340:
        raise RuntimeError(f"Expected a national commune layer, got only {len(features)} features")

    cleaned = []
    for feature in features:
        p = feature.get("properties") or {}
        code = p.get("cod_comuna")
        if code is None:
            continue
        cleaned.append({
            "type": "Feature",
            "properties": {
                "commune_code": int(code),
                "commune": p.get("nom_com"),
                "province": p.get("nom_prov"),
                "region": p.get("nom_reg"),
                "region_code": p.get("codregion"),
            },
            "geometry": feature.get("geometry"),
        })

    cleaned.sort(key=lambda f: f["properties"]["commune_code"])
    codes = [f["properties"]["commune_code"] for f in cleaned]
    if len(codes) != len(set(codes)):
        raise RuntimeError("Duplicate commune codes in source layer")

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(
        json.dumps({"type": "FeatureCollection", "features": cleaned}, ensure_ascii=False, separators=(",", ":")),
        encoding="utf-8",
    )
    print(f"Wrote {len(cleaned)} commune features to {OUT}")


if __name__ == "__main__":
    main()
