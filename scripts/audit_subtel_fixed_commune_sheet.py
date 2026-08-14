from __future__ import annotations

import csv
import io
from pathlib import Path

import openpyxl
import requests

URL = "https://www.subtel.gob.cl/wp-content/uploads/2026/05/1_SERIES_CONEXIONES_INTERNET_FIJA_MAR26_040526.xlsx"
OUT = Path("data/subtel_sector_series/fixed_commune_sheet_audit.csv")
SHEET = "7.11.CO_FIJAS_COMUNA"
YEAR = 2026
MONTH_NAMES = {"mar", "marzo"}


def clean(v):
    return "" if v is None else str(v).strip().replace("\n", " ")


def locate_period_column(ws):
    current_year = None
    matches = []
    for col in range(1, ws.max_column + 1):
        y = ws.cell(8, col).value
        if isinstance(y, (int, float)) and int(y) == y and 2000 <= int(y) <= 2100:
            current_year = int(y)
        month = clean(ws.cell(9, col).value).lower()
        if current_year == YEAR and month in MONTH_NAMES:
            matches.append(col)
    if not matches:
        raise RuntimeError("Could not locate March 2026 column")
    return max(matches)


def main():
    r = requests.get(URL, timeout=180)
    r.raise_for_status()

    wb_values = openpyxl.load_workbook(io.BytesIO(r.content), read_only=False, data_only=True)
    wb_formulas = openpyxl.load_workbook(io.BytesIO(r.content), read_only=False, data_only=False)
    if SHEET not in wb_values.sheetnames:
        raise RuntimeError(f"Expected sheet not found: {SHEET}")

    ws = wb_values[SHEET]
    wsf = wb_formulas[SHEET]
    target_col = locate_period_column(ws)

    formula_rows = []
    suspicious_formula_labels = []
    for row_no in range(10, ws.max_row + 1):
        formula = wsf.cell(row_no, target_col).value
        if isinstance(formula, str) and formula.startswith("="):
            region_label = clean(ws.cell(row_no, 2).value)
            commune_label = clean(ws.cell(row_no, 3).value)
            cached_value = clean(ws.cell(row_no, target_col).value)
            item = (row_no, region_label, commune_label, cached_value, formula)
            formula_rows.append(item)
            if commune_label:
                suspicious_formula_labels.append(item)

    rows = [
        {
            "check": "sheet_present",
            "status": "pass",
            "value": SHEET,
            "detail": "Official March-2026 fixed Internet workbook sheet used for commune-level totals.",
        },
        {
            "check": "march_2026_column",
            "status": "pass",
            "value": str(target_col),
            "detail": f"Column located dynamically from year/month headers ({YEAR}-03).",
        },
        {
            "check": "formula_rows_in_target_column",
            "status": "info",
            "value": str(len(formula_rows)),
            "detail": "Subtotal/total formulas found in the March-2026 column.",
        },
        {
            "check": "formula_rows_with_commune_label",
            "status": "source_warning" if suspicious_formula_labels else "pass",
            "value": str(len(suspicious_formula_labels)),
            "detail": "Formula subtotal/total rows carrying commune labels indicate row-label/value misalignment in the official workbook; do not treat these rows as commune observations.",
        },
    ]

    for row_no, region_label, commune_label, cached_value, formula in suspicious_formula_labels:
        rows.append(
            {
                "check": f"source_row_{row_no}",
                "status": "source_warning",
                "value": cached_value,
                "detail": f"region_label={region_label or '<blank>'}; commune_label={commune_label}; formula={formula}",
            }
        )

    OUT.parent.mkdir(parents=True, exist_ok=True)
    with OUT.open("w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=["check", "status", "value", "detail"])
        w.writeheader()
        w.writerows(rows)

    print("sheet", SHEET)
    print("march_2026_column", target_col)
    print("formula_rows", len(formula_rows))
    print("formula_rows_with_commune_label", len(suspicious_formula_labels))
    if suspicious_formula_labels:
        print("SOURCE WARNING: official workbook contains subtotal/total formulas on rows carrying commune labels.")
        for item in suspicious_formula_labels:
            print(item)


if __name__ == "__main__":
    main()
