#!/usr/bin/env python3
"""Discover affordability-related variables in official SUBTEL SAV files.

The script scans recent waves for variables that refer to the cost, price, payment or
monthly spending associated with Internet/connectivity. It publishes metadata only;
raw microdata are never committed.
"""

from __future__ import annotations

import re
import tempfile
import unicodedata
from pathlib import Path

import pandas as pd
import pyreadstat

import profile_subtel_microdata as base

OUT = Path("data/affordability/candidate_variables_2023_2025.csv")
WAVES = {"X": 2023, "XI": 2024, "XII": 2025}

COST_TERMS = [
    "costo", "coste", "precio", "valor", "gasto", "monto", "paga", "pagar",
    "mensual", "mensualidad", "tarifa", "caro", "barato", "asequible",
]
CONTEXT_TERMS = [
    "internet", "conexion", "conexión", "banda ancha", "servicio fijo",
    "servicio movil", "servicio móvil", "plan", "proveedor", "hogar", "wifi",
]
EXCLUDE_TERMS = [
    "pagar cuentas", "pago de cuentas", "pago al estado", "pagos al estado",
    "compras por internet", "transaccion bancaria", "transacción bancaria",
    "medio de pago", "pago online", "comercio electronico", "comercio electrónico",
]


def norm(value: object) -> str:
    text = "" if value is None else str(value)
    text = unicodedata.normalize("NFKD", text)
    text = "".join(c for c in text if not unicodedata.combining(c))
    return re.sub(r"\s+", " ", text).strip().lower()


def score(label: str, variable: str) -> tuple[int, list[str]]:
    text = norm(f"{variable} {label}")
    if any(norm(t) in text for t in EXCLUDE_TERMS):
        return 0, []
    hits = []
    cost_hits = [t for t in COST_TERMS if norm(t) in text]
    context_hits = [t for t in CONTEXT_TERMS if norm(t) in text]
    if not cost_hits:
        return 0, []
    # A cost term plus connectivity context is strongest. Keep some barrier questions
    # whose questionnaire labels may omit 'Internet' because the block itself is about it.
    s = 3 * len(cost_hits) + 2 * len(context_hits)
    if "mensual" in text:
        s += 4
    if "cuanto" in text and ("paga" in text or "gasta" in text):
        s += 5
    if "servicio" in text:
        s += 2
    if context_hits or s >= 7:
        hits = sorted(set(cost_hits + context_hits))
        return s, hits
    return 0, []


def clean_savs(paths):
    return [p for p in paths if p.suffix.lower() == ".sav" and not p.name.startswith("._") and "__MACOSX" not in p.parts]


def main() -> None:
    OUT.parent.mkdir(parents=True, exist_ok=True)
    rows = []
    selected = [s for s in base.SURVEYS if s["wave"] in WAVES]

    with tempfile.TemporaryDirectory() as td:
        workdir = Path(td)
        for spec in selected:
            year = WAVES[spec["wave"]]
            print(f"Scanning {spec['wave']} / {year}")
            for sav in clean_savs(base.extract_sav_files(spec, workdir)):
                try:
                    df, meta = pyreadstat.read_sav(
                        str(sav), apply_value_formats=False, formats_as_category=False, user_missing=False
                    )
                except Exception as exc:
                    print(f"Skipping {sav.name}: {exc!r}")
                    continue
                labels = meta.column_names_to_labels or {}
                value_labels = meta.variable_value_labels or {}
                for col in df.columns:
                    label = labels.get(col, "") or ""
                    s, hits = score(label, col)
                    if not s:
                        continue
                    series = df[col]
                    vals = value_labels.get(col, {}) or {}
                    sample_labels = " | ".join(str(v) for _, v in list(vals.items())[:12])
                    rows.append({
                        "reference_year": year,
                        "survey_wave": spec["wave"],
                        "sav_file": sav.name,
                        "variable": col,
                        "variable_label": label,
                        "score": s,
                        "matched_terms": " | ".join(hits),
                        "nonmissing_n": int(series.notna().sum()),
                        "distinct_nonmissing": int(series.dropna().nunique()),
                        "dtype": str(series.dtype),
                        "numeric": bool(pd.api.types.is_numeric_dtype(series)),
                        "has_value_labels": bool(vals),
                        "sample_value_labels": sample_labels,
                        "source_url": spec["url"],
                    })

    out = pd.DataFrame(rows)
    if out.empty:
        raise RuntimeError("No affordability candidates found")
    out = out.sort_values(["reference_year", "score", "variable"], ascending=[True, False, True]).reset_index(drop=True)
    out.to_csv(OUT, index=False)
    print(f"Wrote {len(out)} affordability candidates to {OUT}")
    for year, g in out.groupby("reference_year"):
        print("\nYEAR", year)
        print(g.head(20)[["variable", "variable_label", "score", "distinct_nonmissing", "sample_value_labels"]].to_string(index=False))


if __name__ == "__main__":
    main()
