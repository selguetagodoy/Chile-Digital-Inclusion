#!/usr/bin/env python3
"""Promote verified Ookla Q2 2026 outputs to current release references.

This script only performs explicit text substitutions after Q2 national and
territorial QA have succeeded. Historical Q1 data files remain in the repo.
"""

from pathlib import Path


def replace_all(path: str, replacements: list[tuple[str, str]]) -> None:
    p = Path(path)
    text = p.read_text(encoding="utf-8")
    original = text
    for old, new in replacements:
        if old not in text:
            print(f"WARN {path}: pattern not found: {old}")
        text = text.replace(old, new)
    if text != original:
        p.write_text(text, encoding="utf-8")
        print(f"updated {path}")
    else:
        print(f"unchanged {path}")


replace_all("assets/dashboard.js", [
    ("sector_snapshot_2026q1.csv", "sector_snapshot_2026q2.csv"),
    ("2026q1", "2026q2"),
    ("Q1 2026", "Q2 2026"),
    ("2026m03", "2026m06"),
    ("mar 2026", "jun 2026"),
])

replace_all("scripts/validate_public_release.py", [
    ("commune_fixed_connections_2026_03.csv", "commune_fixed_connections_2026_06.csv"),
    ("sector_snapshot_2026q1.csv", "sector_snapshot_2026q2.csv"),
    ("chile_2026q1_summary.csv", "chile_2026q2_summary.csv"),
    ("ookla_fixed_download_mbps_2026q1", "ookla_fixed_download_mbps_2026q2"),
    ("ookla_mobile_download_mbps_2026q1", "ookla_mobile_download_mbps_2026q2"),
    ("len(master_fields) == 94", "len(master_fields) == 117"),
    ("94 variables", "117 variables"),
    ("sector_snapshot_2026q1.csv", "sector_snapshot_2026q2.csv"),
    ("subtel_fixed_residential_per_100_censo_households_2026m03", "subtel_fixed_residential_per_100_censo_households_2026m06"),
])

replace_all("scripts/build_release_metadata.py", [
    ("'layer_id': 'ookla_national_2026q1', 'path': 'data/ookla/chile_2026q1_summary.csv', 'source_family': 'Ookla Open Data', 'reference_period': '2026Q1'",
     "'layer_id': 'ookla_national_2026q2', 'path': 'data/ookla/chile_2026q2_summary.csv', 'source_family': 'Ookla Open Data', 'reference_period': '2026Q2'"),
    ("'layer_id': 'ookla_communal_2026q1', 'path': 'data/ookla/territorial/chile_2026q1_communes.csv', 'source_family': 'Ookla Open Data', 'reference_period': '2026Q1'",
     "'layer_id': 'ookla_communal_2026q2', 'path': 'data/ookla/territorial/chile_2026q2_communes.csv', 'source_family': 'Ookla Open Data', 'reference_period': '2026Q2'"),
])

print("Q2 promotion references patched")
