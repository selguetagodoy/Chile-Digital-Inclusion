#!/usr/bin/env python3
"""Append Q3 to previously published national longitudinal Ookla data."""
import csv
from pathlib import Path
old = Path("data/ookla/chile_2024q1_2026q2_longitudinal.csv")
q3 = Path("data/ookla/chile_2026q3_summary.csv")
dst = Path("data/ookla/chile_2024q1_2026q3_longitudinal.csv")
with old.open(encoding="utf-8", newline="") as f:
    reader = csv.DictReader(f)
    fields = reader.fieldnames
    rows = list(reader)
assert len(rows) == 20 and rows[-1]["period"] == "2026Q2"
prev = {r["network"]: r for r in rows if r["period"] == "2026Q2"}
with q3.open(encoding="utf-8", newline="") as f:
    fresh = list(csv.DictReader(f))
assert {r["network"] for r in fresh} == {"fixed", "mobile"}
for cur in fresh:
    row = {k: cur.get(k, "") for k in fields}
    row["period"] = "2026Q3"
    for metric in ("download", "upload", "latency"):
        key = metric + "_mbps_test_weighted" if metric != "latency" else "latency_ms_test_weighted"
        oldv = float(prev[cur["network"]][key])
        newv = float(cur[key])
        row[metric + "_qoq_pct"] = round((newv - oldv) / oldv * 100, 3) if oldv else ""
    rows.append(row)
assert len(rows) == 22
with dst.open("w", encoding="utf-8", newline="") as f:
    w = csv.DictWriter(f, fieldnames=fields)
    w.writeheader()
    w.writerows(rows)
print("Built", dst, len(rows))
