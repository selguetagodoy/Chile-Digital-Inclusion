#!/usr/bin/env python3
"""Validate public, source-traced telecom financial observations."""
import csv
from datetime import date
from decimal import Decimal, InvalidOperation
from pathlib import Path
from urllib.parse import urlparse

FILE = Path(__file__).resolve().parents[1] / "data/economics/telecom_financials_2024_2026.csv"
REQUIRED = (
    "company", "reported_entity", "scope", "geography", "period", "period_start",
    "period_end", "period_kind", "ebitda_basis", "revenue_clp_mm", "ebitda_clp_mm",
    "ebitda_margin_pct", "capex_clp_mm", "ebit_clp_mm", "net_income_clp_mm",
    "reported_leverage_ratio_x", "source_class", "source_url", "source_published",
    "status", "notes",
)
NUMERIC = (
    "revenue_clp_mm", "ebitda_clp_mm", "ebitda_margin_pct", "capex_clp_mm",
    "ebit_clp_mm", "net_income_clp_mm", "reported_leverage_ratio_x",
)
GRAINS = {"Q1", "Q2", "Q3", "Q4", "H1", "9M", "FY"}
LATEST_CUTOFF = date(2026, 10, 29)


def check():
    failures = []
    seen = set()
    with FILE.open(newline="", encoding="utf-8-sig") as fh:
        reader = csv.DictReader(fh)
        if tuple(reader.fieldnames or ()) != REQUIRED:
            failures.append("CSV columns must match documented contract and order")
        rows = list(reader)

    for i, row in enumerate(rows, start=2):
        prefix = f"line {i}"
        key = (row.get("company"), row.get("scope"), row.get("period"))
        if not all(key):
            failures.append(f"{prefix}: missing analytical key")
        elif key in seen:
            failures.append(f"{prefix}: duplicate company/scope/period {key!r}")
        seen.add(key)

        if row.get("period_kind") not in GRAINS:
            failures.append(f"{prefix}: invalid period kind")
        if row.get("status") != "actual":
            failures.append(f"{prefix}: historical dataset must contain only actual values")
        if not row.get("reported_entity") or not row.get("geography"):
            failures.append(f"{prefix}: missing entity or geographic perimeter")
        if not row.get("ebitda_basis") or not row.get("source_class"):
            failures.append(f"{prefix}: missing financial definition or source type")
        if not row.get("notes"):
            failures.append(f"{prefix}: missing provenance qualification")

        try:
            start = date.fromisoformat(row["period_start"])
            end = date.fromisoformat(row["period_end"])
            if start > end or end > LATEST_CUTOFF:
                failures.append(f"{prefix}: invalid or future period")
        except (KeyError, TypeError, ValueError):
            failures.append(f"{prefix}: unparseable period dates")

        if row.get("source_published"):
            try:
                published = date.fromisoformat(row["source_published"])
                if published > LATEST_CUTOFF:
                    failures.append(f"{prefix}: future publication date")
            except ValueError:
                failures.append(f"{prefix}: unparseable publication date")

        url = urlparse(row.get("source_url") or "")
        if url.scheme != "https" or not url.netloc:
            failures.append(f"{prefix}: invalid source URL")

        vals = {}
        for field in NUMERIC:
            value = row.get(field, "")
            if value is None or not value.strip():
                continue
            try:
                vals[field] = Decimal(value)
                if not vals[field].is_finite():
                    failures.append(f"{prefix}: invalid finite value for {field}")
            except InvalidOperation:
                failures.append(f"{prefix}: nonnumeric {field}")

        if vals.get("revenue_clp_mm", Decimal(0)) < 0:
            failures.append(f"{prefix}: negative revenue")
        if "ebitda_margin_pct" in vals and "ebitda_clp_mm" in vals and "revenue_clp_mm" in vals:
            if vals["revenue_clp_mm"] == 0:
                failures.append(f"{prefix}: cannot compute margin on zero revenue")
            else:
                computed = Decimal(100) * vals["ebitda_clp_mm"] / vals["revenue_clp_mm"]
                if abs(computed - vals["ebitda_margin_pct"]) > Decimal("0.25"):
                    failures.append(f"{prefix}: EBITDA margin not reconciled (reported {vals['ebitda_margin_pct']}, computed {computed:.3f})")

        if row.get("scope") == "chile_revenue_segment" and (
            row.get("ebitda_clp_mm") or row.get("capex_clp_mm") or row.get("ebitda_margin_pct")
        ):
            failures.append(f"{prefix}: do not impute international group EBITDA/CAPEX to Chile")
        if row.get("scope") == "southern_cone_segment" and "Paraguay" not in row.get("geography", ""):
            failures.append(f"{prefix}: Cono Sur should be identified as non-Chile-only")
        if row.get("company") == "Mundo" and row.get("ebitda_basis") != "sp_global_ratings_adjusted":
            failures.append(f"{prefix}: Mundo EBITDA must retain ratings adjustments")

    if not rows:
        failures.append("Financial dataset is empty")
    if failures:
        print("\n".join("FAIL: " + msg for msg in failures))
        raise SystemExit(1)
    print(f"OK: {len(rows)} financial observations, {len(seen)} unique keys, 0 issues")


if __name__ == "__main__":
    check()
