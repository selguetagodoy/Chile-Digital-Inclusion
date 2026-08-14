#!/usr/bin/env python3

import argparse
import csv
import io
import math
import os
import tempfile
import zipfile
from datetime import date
from pathlib import Path

import duckdb
import fiona
import numpy as np
import pyarrow as pa
import pyarrow.csv as pacsv
import requests
from shapely import contains_xy
from shapely.geometry import shape
from shapely.ops import unary_union

OOKLA_ROOT = "https://ookla-open-data.s3.amazonaws.com/parquet/performance"
NATURAL_EARTH = "https://naturalearth.s3.amazonaws.com/10m_cultural/ne_10m_admin_0_countries.zip"
BBOX = (-76.5, -56.5, -65.0, -16.5)  # west, south, east, north


def quarter_start(year: int, quarter: int) -> str:
    month = 1 + (quarter - 1) * 3
    return f"{year:04d}-{month:02d}-01"


def ookla_url(year: int, quarter: int, network: str) -> str:
    start = quarter_start(year, quarter)
    return (
        f"{OOKLA_ROOT}/type={network}/year={year}/quarter={quarter}/"
        f"{start}_performance_{network}_tiles.parquet"
    )


def load_chile_geometry():
    r = requests.get(NATURAL_EARTH, timeout=120)
    r.raise_for_status()
    with tempfile.TemporaryDirectory() as td:
        zpath = Path(td) / "ne.zip"
        zpath.write_bytes(r.content)
        with zipfile.ZipFile(zpath) as zf:
            zf.extractall(td)
        shp = next(Path(td).glob("*.shp"))
        geometries = []
        with fiona.open(shp) as src:
            for feature in src:
                props = feature["properties"]
                code = props.get("ADM0_A3") or props.get("ISO_A3") or props.get("SOV_A3")
                if code == "CHL":
                    geometries.append(shape(feature["geometry"]))
        if not geometries:
            raise RuntimeError("Chile geometry not found in Natural Earth ADM0 dataset")
        return unary_union(geometries)


def query_bbox(url: str) -> pa.Table:
    west, south, east, north = BBOX
    con = duckdb.connect()
    con.execute("INSTALL httpfs")
    con.execute("LOAD httpfs")
    query = f"""
        SELECT
            quadkey,
            tile_x,
            tile_y,
            avg_d_kbps / 1000.0 AS avg_d_mbps,
            avg_u_kbps / 1000.0 AS avg_u_mbps,
            avg_lat_ms,
            avg_lat_down_ms,
            avg_lat_up_ms,
            tests,
            devices
        FROM read_parquet('{url}')
        WHERE tile_x BETWEEN {west} AND {east}
          AND tile_y BETWEEN {south} AND {north}
    """
    table = con.execute(query).fetch_arrow_table()
    con.close()
    return table


def clip_to_chile(table: pa.Table, chile_geom) -> pa.Table:
    xs = table["tile_x"].to_numpy(zero_copy_only=False)
    ys = table["tile_y"].to_numpy(zero_copy_only=False)
    mask = contains_xy(chile_geom, xs, ys)
    return table.filter(pa.array(mask))


def weighted_mean(values, weights):
    v = np.asarray(values, dtype=float)
    w = np.asarray(weights, dtype=float)
    valid = np.isfinite(v) & np.isfinite(w) & (w > 0)
    if not valid.any():
        return math.nan
    return float(np.average(v[valid], weights=w[valid]))


def summarize(table: pa.Table, year: int, quarter: int, network: str, source_url: str):
    tests = table["tests"].to_numpy(zero_copy_only=False)
    devices = table["devices"].to_numpy(zero_copy_only=False)
    row = {
        "year": year,
        "quarter": quarter,
        "network": network,
        "tiles": table.num_rows,
        "tests": int(np.nansum(tests)),
        "devices_sum_across_tiles": int(np.nansum(devices)),
        "download_mbps_test_weighted": round(weighted_mean(table["avg_d_mbps"].to_numpy(zero_copy_only=False), tests), 3),
        "upload_mbps_test_weighted": round(weighted_mean(table["avg_u_mbps"].to_numpy(zero_copy_only=False), tests), 3),
        "latency_ms_test_weighted": round(weighted_mean(table["avg_lat_ms"].to_numpy(zero_copy_only=False), tests), 3),
        "loaded_latency_down_ms_test_weighted": round(weighted_mean(table["avg_lat_down_ms"].to_numpy(zero_copy_only=False), tests), 3),
        "loaded_latency_up_ms_test_weighted": round(weighted_mean(table["avg_lat_up_ms"].to_numpy(zero_copy_only=False), tests), 3),
        "aggregation": "tile averages weighted by tile test count",
        "spatial_filter": "tile centroid within Natural Earth 10m Chile ADM0",
        "source_url": source_url,
    }
    return row


def write_summary(rows, path: Path):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def build_period(year: int, quarter: int, chile_geom, output_dir: Path, keep_tiles: bool):
    summaries = []
    tile_tables = {}
    for network in ("fixed", "mobile"):
        url = ookla_url(year, quarter, network)
        print(f"Reading {network} {year} Q{quarter}: {url}")
        bbox = query_bbox(url)
        clipped = clip_to_chile(bbox, chile_geom)
        clipped = clipped.sort_by([("quadkey", "ascending")])
        summaries.append(summarize(clipped, year, quarter, network, url))
        tile_tables[network] = clipped
        if keep_tiles:
            out = output_dir / f"chile_{year}q{quarter}_{network}_tiles.csv"
            pacsv.write_csv(clipped, out)
            print(f"Wrote {out} ({clipped.num_rows} tiles)")
    return summaries, tile_tables


def write_comparison(control_rows, current_rows, path: Path):
    by_network = {r["network"]: r for r in control_rows}
    fields = [
        "network",
        "control_period",
        "current_period",
        "control_download_mbps",
        "current_download_mbps",
        "download_delta_mbps",
        "download_delta_pct",
        "control_upload_mbps",
        "current_upload_mbps",
        "upload_delta_mbps",
        "upload_delta_pct",
        "control_latency_ms",
        "current_latency_ms",
        "latency_delta_ms",
        "latency_delta_pct",
        "control_tests",
        "current_tests",
    ]
    rows = []
    for cur in current_rows:
        old = by_network[cur["network"]]
        def delta(a, b):
            d = b - a
            p = (d / a * 100.0) if a else math.nan
            return round(d, 3), round(p, 3)
        dd, dp = delta(old["download_mbps_test_weighted"], cur["download_mbps_test_weighted"])
        ud, up = delta(old["upload_mbps_test_weighted"], cur["upload_mbps_test_weighted"])
        ld, lp = delta(old["latency_ms_test_weighted"], cur["latency_ms_test_weighted"])
        rows.append({
            "network": cur["network"],
            "control_period": f"{old['year']}Q{old['quarter']}",
            "current_period": f"{cur['year']}Q{cur['quarter']}",
            "control_download_mbps": old["download_mbps_test_weighted"],
            "current_download_mbps": cur["download_mbps_test_weighted"],
            "download_delta_mbps": dd,
            "download_delta_pct": dp,
            "control_upload_mbps": old["upload_mbps_test_weighted"],
            "current_upload_mbps": cur["upload_mbps_test_weighted"],
            "upload_delta_mbps": ud,
            "upload_delta_pct": up,
            "control_latency_ms": old["latency_ms_test_weighted"],
            "current_latency_ms": cur["latency_ms_test_weighted"],
            "latency_delta_ms": ld,
            "latency_delta_pct": lp,
            "control_tests": old["tests"],
            "current_tests": cur["tests"],
        })
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--year", type=int, required=True)
    parser.add_argument("--quarter", type=int, choices=(1, 2, 3, 4), required=True)
    parser.add_argument("--compare-year", type=int, default=None)
    parser.add_argument("--compare-quarter", type=int, choices=(1, 2, 3, 4), default=None)
    parser.add_argument("--output-dir", default="data/ookla")
    args = parser.parse_args()

    outdir = Path(args.output_dir)
    outdir.mkdir(parents=True, exist_ok=True)
    chile = load_chile_geometry()

    current, _ = build_period(args.year, args.quarter, chile, outdir, keep_tiles=True)
    write_summary(current, outdir / f"chile_{args.year}q{args.quarter}_summary.csv")

    if args.compare_year and args.compare_quarter:
        control, _ = build_period(args.compare_year, args.compare_quarter, chile, outdir, keep_tiles=False)
        write_summary(control, outdir / f"chile_{args.compare_year}q{args.compare_quarter}_control_summary.csv")
        write_comparison(control, current, outdir / f"chile_{args.compare_year}q{args.compare_quarter}_vs_{args.year}q{args.quarter}.csv")


if __name__ == "__main__":
    main()
