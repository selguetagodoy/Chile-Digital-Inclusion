#!/usr/bin/env python3
"""Aggregate Ookla tile observations to Chilean communes and regions.

The script uses tile centroids already filtered to Chile. It performs a point-in-polygon
join against the public communal GeoJSON, weights tile averages by the number of tests,
and writes current-period, comparison and integrated communal products.
"""

from __future__ import annotations

import argparse
from pathlib import Path

import geopandas as gpd
import numpy as np
import pandas as pd

METRICS = ["avg_d_mbps", "avg_u_mbps", "avg_lat_ms", "avg_lat_down_ms", "avg_lat_up_ms"]


def weighted_mean(values: pd.Series, weights: pd.Series) -> float:
    v = pd.to_numeric(values, errors="coerce").to_numpy(dtype=float)
    w = pd.to_numeric(weights, errors="coerce").to_numpy(dtype=float)
    valid = np.isfinite(v) & np.isfinite(w) & (w > 0)
    if not valid.any():
        return np.nan
    return float(np.average(v[valid], weights=w[valid]))


def read_tiles(path: Path, network: str, period: str) -> pd.DataFrame:
    df = pd.read_csv(path)
    required = {"tile_x", "tile_y", "tests", "devices", *METRICS}
    missing = sorted(required - set(df.columns))
    if missing:
        raise RuntimeError(f"{path} is missing required columns: {missing}")
    df["network"] = network
    df["period"] = period
    return df


def spatial_join(tiles: pd.DataFrame, communes: gpd.GeoDataFrame) -> tuple[gpd.GeoDataFrame, dict]:
    points = gpd.GeoDataFrame(
        tiles.copy(),
        geometry=gpd.points_from_xy(tiles["tile_x"], tiles["tile_y"]),
        crs="EPSG:4326",
    )
    cols = ["commune_code", "commune", "province", "region", "region_code", "geometry"]
    joined = gpd.sjoin(points, communes[cols], how="left", predicate="within")

    matched = joined["commune_code"].notna()
    total_tests = float(pd.to_numeric(joined["tests"], errors="coerce").fillna(0).sum())
    matched_tests = float(pd.to_numeric(joined.loc[matched, "tests"], errors="coerce").fillna(0).sum())
    coverage = {
        "period": str(joined["period"].iloc[0]),
        "network": str(joined["network"].iloc[0]),
        "tiles_total": int(len(joined)),
        "tiles_assigned_to_commune": int(matched.sum()),
        "tile_assignment_pct": round(float(matched.mean() * 100), 3),
        "tests_total": int(total_tests),
        "tests_assigned_to_commune": int(matched_tests),
        "test_assignment_pct": round((matched_tests / total_tests * 100.0) if total_tests else np.nan, 3),
        "spatial_method": "Ookla tile centroid within BCN commune polygon",
    }
    return joined.loc[matched].copy(), coverage


def summarize(joined: pd.DataFrame, keys: list[str]) -> pd.DataFrame:
    rows = []
    for group_key, g in joined.groupby(keys, dropna=False, sort=True):
        if not isinstance(group_key, tuple):
            group_key = (group_key,)
        row = dict(zip(keys, group_key))
        row.update({
            "period": str(g["period"].iloc[0]),
            "network": str(g["network"].iloc[0]),
            "tiles": int(len(g)),
            "tests": int(pd.to_numeric(g["tests"], errors="coerce").fillna(0).sum()),
            "devices_sum_across_tiles": int(pd.to_numeric(g["devices"], errors="coerce").fillna(0).sum()),
            "download_mbps_test_weighted": round(weighted_mean(g["avg_d_mbps"], g["tests"]), 3),
            "upload_mbps_test_weighted": round(weighted_mean(g["avg_u_mbps"], g["tests"]), 3),
            "latency_ms_test_weighted": round(weighted_mean(g["avg_lat_ms"], g["tests"]), 3),
            "loaded_latency_down_ms_test_weighted": round(weighted_mean(g["avg_lat_down_ms"], g["tests"]), 3),
            "loaded_latency_up_ms_test_weighted": round(weighted_mean(g["avg_lat_up_ms"], g["tests"]), 3),
            "aggregation": "tile averages weighted by tile test count",
        })
        rows.append(row)
    return pd.DataFrame(rows)


def add_delta(df: pd.DataFrame, metric: str) -> None:
    a = pd.to_numeric(df[f"control_{metric}"], errors="coerce")
    b = pd.to_numeric(df[f"current_{metric}"], errors="coerce")
    df[f"delta_{metric}"] = (b - a).round(3)
    df[f"delta_pct_{metric}"] = np.where(a.notna() & (a != 0) & b.notna(), ((b - a) / a * 100.0).round(3), np.nan)


def comparison(control: pd.DataFrame, current: pd.DataFrame, keys: list[str]) -> pd.DataFrame:
    keep_metrics = [
        "tiles", "tests", "devices_sum_across_tiles",
        "download_mbps_test_weighted", "upload_mbps_test_weighted", "latency_ms_test_weighted",
        "loaded_latency_down_ms_test_weighted", "loaded_latency_up_ms_test_weighted",
    ]
    left = control[keys + ["period"] + keep_metrics].rename(
        columns={"period": "control_period", **{c: f"control_{c}" for c in keep_metrics}}
    )
    right = current[keys + ["period"] + keep_metrics].rename(
        columns={"period": "current_period", **{c: f"current_{c}" for c in keep_metrics}}
    )
    out = left.merge(right, on=keys, how="outer")
    for metric in ["download_mbps_test_weighted", "upload_mbps_test_weighted", "latency_ms_test_weighted"]:
        add_delta(out, metric)
    return out.sort_values(keys).reset_index(drop=True)


def build_integrated_master(base_path: Path, current_communes: pd.DataFrame, comp_communes: pd.DataFrame) -> pd.DataFrame:
    base = pd.read_csv(base_path)
    if "comuna" not in base.columns:
        raise RuntimeError("Base communal master must contain numeric 'comuna' code")
    base["comuna"] = pd.to_numeric(base["comuna"], errors="coerce").astype("Int64")

    frames = []
    for network in ("fixed", "mobile"):
        cur = current_communes[current_communes["network"] == network].copy()
        prefix = f"ookla_{network}_"
        cur = cur.rename(columns={
            "commune_code": "comuna",
            "tiles": prefix + "tiles_2026q1",
            "tests": prefix + "tests_2026q1",
            "devices_sum_across_tiles": prefix + "devices_sum_2026q1",
            "download_mbps_test_weighted": prefix + "download_mbps_2026q1",
            "upload_mbps_test_weighted": prefix + "upload_mbps_2026q1",
            "latency_ms_test_weighted": prefix + "latency_ms_2026q1",
            "loaded_latency_down_ms_test_weighted": prefix + "loaded_latency_down_ms_2026q1",
            "loaded_latency_up_ms_test_weighted": prefix + "loaded_latency_up_ms_2026q1",
        })
        keep = ["comuna"] + [c for c in cur.columns if c.startswith(prefix)]
        frames.append(cur[keep])

        cmpn = comp_communes[comp_communes["network"] == network].copy()
        cmpn = cmpn.rename(columns={
            "commune_code": "comuna",
            "delta_pct_download_mbps_test_weighted": prefix + "download_delta_pct_q4_to_q1",
            "delta_pct_upload_mbps_test_weighted": prefix + "upload_delta_pct_q4_to_q1",
            "delta_pct_latency_ms_test_weighted": prefix + "latency_delta_pct_q4_to_q1",
            "control_tests": prefix + "tests_2025q4",
        })
        keep_cmp = ["comuna"] + [c for c in cmpn.columns if c.startswith(prefix)]
        frames.append(cmpn[keep_cmp])

    out = base.copy()
    for frame in frames:
        frame["comuna"] = pd.to_numeric(frame["comuna"], errors="coerce").astype("Int64")
        out = out.merge(frame, on="comuna", how="left")

    fixed_tests = pd.to_numeric(out.get("ookla_fixed_tests_2026q1"), errors="coerce").fillna(0)
    mobile_tests = pd.to_numeric(out.get("ookla_mobile_tests_2026q1"), errors="coerce").fillna(0)
    out["ookla_observed_any_2026q1"] = np.where((fixed_tests + mobile_tests) > 0, "yes", "no")
    out["ookla_period"] = "2026Q1"
    out["ookla_spatial_method"] = "tile centroid within BCN commune polygon"
    return out


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--current-fixed", required=True)
    p.add_argument("--current-mobile", required=True)
    p.add_argument("--control-fixed", required=True)
    p.add_argument("--control-mobile", required=True)
    p.add_argument("--geo", default="geo/chile_communes.geojson")
    p.add_argument("--base-master", default="data/communal_master/chile_digital_inclusion_communes_2026.csv")
    p.add_argument("--output-dir", default="data/ookla/territorial")
    p.add_argument("--integrated-master", default="data/communal_master/chile_digital_inclusion_communes_2026_integrated.csv")
    args = p.parse_args()

    outdir = Path(args.output_dir)
    outdir.mkdir(parents=True, exist_ok=True)
    communes = gpd.read_file(args.geo).to_crs("EPSG:4326")
    communes["commune_code"] = pd.to_numeric(communes["commune_code"], errors="coerce").astype("Int64")

    specs = [
        (Path(args.control_fixed), "fixed", "2025Q4"),
        (Path(args.control_mobile), "mobile", "2025Q4"),
        (Path(args.current_fixed), "fixed", "2026Q1"),
        (Path(args.current_mobile), "mobile", "2026Q1"),
    ]

    commune_parts, region_parts, coverage_rows = [], [], []
    for path, network, period in specs:
        tiles = read_tiles(path, network, period)
        joined, coverage = spatial_join(tiles, communes)
        coverage_rows.append(coverage)
        commune_parts.append(summarize(joined, ["commune_code", "commune", "province", "region", "region_code"]))
        region_parts.append(summarize(joined, ["region_code", "region"]))

    communes_all = pd.concat(commune_parts, ignore_index=True)
    regions_all = pd.concat(region_parts, ignore_index=True)
    current_communes = communes_all[communes_all["period"] == "2026Q1"].copy()
    control_communes = communes_all[communes_all["period"] == "2025Q4"].copy()
    current_regions = regions_all[regions_all["period"] == "2026Q1"].copy()
    control_regions = regions_all[regions_all["period"] == "2025Q4"].copy()

    comp_communes = comparison(control_communes, current_communes, ["commune_code", "commune", "province", "region", "region_code", "network"])
    comp_regions = comparison(control_regions, current_regions, ["region_code", "region", "network"])

    current_communes.to_csv(outdir / "chile_2026q1_communes.csv", index=False)
    current_regions.to_csv(outdir / "chile_2026q1_regions.csv", index=False)
    comp_communes.to_csv(outdir / "chile_2025q4_vs_2026q1_communes.csv", index=False)
    comp_regions.to_csv(outdir / "chile_2025q4_vs_2026q1_regions.csv", index=False)
    pd.DataFrame(coverage_rows).to_csv(outdir / "spatial_assignment_coverage.csv", index=False)

    integrated = build_integrated_master(Path(args.base_master), current_communes, comp_communes)
    Path(args.integrated_master).parent.mkdir(parents=True, exist_ok=True)
    integrated.to_csv(args.integrated_master, index=False)

    print(f"Current commune rows: {len(current_communes)}")
    print(f"Current region rows: {len(current_regions)}")
    print(f"Integrated master: {len(integrated)} communes, {len(integrated.columns)} columns")


if __name__ == "__main__":
    main()
