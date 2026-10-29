#!/usr/bin/env python3
"""Promote validated Q3 Ookla layers while retaining historical and SUBTEL datasets."""
import csv
from collections import Counter
from pathlib import Path

MASTER = Path("data/communal_master/chile_digital_inclusion_communes_2026_integrated.csv")
DICT = Path("data/metadata/communal_master_dictionary.csv")

with MASTER.open(encoding="utf-8", newline="") as f:
    rd = csv.DictReader(f)
    master_cols, master_rows = rd.fieldnames, list(rd)
assert len(master_rows) == 346, len(master_rows)
assert len(master_cols) == 140, len(master_cols)
assert {r["ookla_period"] for r in master_rows} == {"2026Q3"}

with DICT.open(encoding="utf-8-sig", newline="") as f:
    rd = csv.DictReader(f)
    fields, rows = rd.fieldnames, list(rd)
bycol = {r["variable"]: r for r in rows}
for col in master_cols:
    if col in bycol:
        continue
    prev = col.replace("_2026q3", "_2026q2").replace("_q2_to_q3", "_q1_to_q2")
    if prev not in bycol:
        raise RuntimeError(f"Dictionary lacks template {prev} for {col}")
    row = {k: v.replace("2026q2", "2026q3").replace("Q2 2026", "Q3 2026")
           .replace("Q1→Q2", "Q2→Q3").replace("Q1 a Q2", "Q2 a Q3")
           for k, v in bycol[prev].items()}
    row["variable"] = col
    rows.append(row)
    bycol[col] = row
assert set(bycol) == set(master_cols), (set(master_cols)-set(bycol),set(bycol)-set(master_cols))
with DICT.open("w", encoding="utf-8", newline="") as f:
    w = csv.DictWriter(f, fieldnames=fields)
    w.writeheader()
    w.writerows(rows)

doc = Path("docs/communal_master_dictionary.md")
txt = doc.read_text(encoding="utf-8")
txt = txt.replace("117 variables", "140 variables")
txt = txt.replace("Ookla Open Data: 49", f"Ookla Open Data: {Counter(r['source_layer'] for r in rows)['Ookla Open Data']}")
txt = txt.replace("Última revisión: 2026-08-14", "Última revisión: 2026-10-29")
doc.write_text(txt, encoding="utf-8")

# The SUBTEL Q2 2026 snapshot is not an Ookla quarter: leave it untouched.
js = Path("assets/dashboard.js")
lines = []
for line in js.read_text(encoding="utf-8").splitlines(keepends=True):
    if "ookla_" in line or "Ookla Q2 2026" in line:
        line = line.replace("2026q2", "2026q3").replace("Ookla Q2 2026", "Ookla Q3 2026")
    lines.append(line)
js.write_text("".join(lines), encoding="utf-8")

p = Path("scripts/validate_public_release.py")
s = p.read_text(encoding="utf-8")
s = s.replace("data/ookla/chile_2026q2_summary.csv", "data/ookla/chile_2026q3_summary.csv")
s = s.replace("len(master_fields) == 117", "len(master_fields) == 140")
needle = "    'ookla_fixed_download_mbps_2026q2', 'ookla_mobile_download_mbps_2026q2',"
if "    'ookla_fixed_download_mbps_2026q3', 'ookla_mobile_download_mbps_2026q3'," not in s:
    assert needle in s
    s = s.replace(needle, needle + "\n    'ookla_fixed_download_mbps_2026q3', 'ookla_mobile_download_mbps_2026q3',")
p.write_text(s, encoding="utf-8")

p = Path("scripts/build_release_metadata.py")
s = p.read_text(encoding="utf-8")
lines = []
for line in s.splitlines(keepends=True):
    if "'layer_id': 'ookla_" in line and "2026q2" in line:
        line = line.replace("2026q2", "2026q3").replace("2026Q2", "2026Q3")
    lines.append(line)
p.write_text("".join(lines), encoding="utf-8")

p = Path("scripts/validate_release_metadata.py")
s = p.read_text(encoding="utf-8")
s = s.replace("ookla_national_2026q2", "ookla_national_2026q3")
s = s.replace("ookla_communal_2026q2", "ookla_communal_2026q3")
s = s.replace("require_shape(catalog, 'communal_master_2026', 346, 117)",
              "require_shape(catalog, 'communal_master_2026', 346, 140)")
needle = "    require_shape(catalog, 'ookla_communal_2026q3', 683, 16)"
# Idempotent migration: a prior run may have already replaced this validator.
replacement = (
    "    q3_n = len(read_csv(Path('data/ookla/territorial/chile_2026q3_communes.csv')))\n"
    "    if not 600 <= q3_n <= 700:\n"
    "        raise RuntimeError(f'Unexpected Q3 commune-network rows: {q3_n}')\n"
    "    require_shape(catalog, 'ookla_communal_2026q3', q3_n, 16)"
)
p.write_text(s.replace(needle, replacement) if needle in s else s, encoding="utf-8")

with Path("data/ookla/chile_2026q3_summary.csv").open(encoding="utf-8", newline="") as f:
    summary = list(csv.DictReader(f))
assert len(summary) == 2 and {r["network"] for r in summary} == {"fixed","mobile"}
readme = Path("README.md")
s = readme.read_text(encoding="utf-8")
s = s.replace("117 variables", "140 variables")
s = s.replace("### Calidad observada — Ookla Q1–Q2 2026",
              "### Calidad observada — Ookla Q1–Q3 2026")
marker = "### Ookla Q3 2026 — julio a septiembre"
if marker not in s:
    s += "\n\n" + marker + "\n\n"
    s += ("Nuevas observaciones de Ookla Open Data publicadas el 9 de octubre de 2026; "
          "promedios nacionales ponderados por tests y asignación territorial por centroide "
          "a polígonos BCN. No son estimaciones de cobertura ni de penetración.\n\n")
    s += "| Red | Descarga (Mbps) | Carga (Mbps) | Latencia (ms) | Tests |\n"
    s += "|---|---:|---:|---:|---:|\n"
    for row in summary:
        s += (f"| {row['network']} | {float(row['download_mbps_test_weighted']):.2f} | "
              f"{float(row['upload_mbps_test_weighted']):.2f} | "
              f"{float(row['latency_ms_test_weighted']):.2f} | {row['tests']} |\n")
    s += ("\nDatos publicados en data/ookla: resumen Q3, control Q2–Q3, serie 2024Q1–2026Q3, "
          "agregados comunales y regionales Q3, comparación territorial y rankings; "
          "se conservan todos los archivos históricos Q1 y Q2.\n")
readme.write_text(s, encoding="utf-8")
print("Q3 promoted", len(master_rows), len(master_cols), len(rows))
