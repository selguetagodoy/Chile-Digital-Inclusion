#!/usr/bin/env python3
"""Build conservative SUBTEL affordability indicators for 2023-2025.

Outputs are demand-side affordability evidence, not market tariffs:
- maximum willingness to pay for household Internet connection;
- reported cost barriers among households without paid fixed broadband.

Official SAV files are downloaded temporarily and only aggregates are committed.
"""

from __future__ import annotations

import tempfile
import unicodedata
from pathlib import Path

import numpy as np
import pandas as pd
import pyreadstat

import profile_subtel_microdata as base

OUTDIR = Path("data/affordability")

WAVES = {
    "X": {
        "year": 2023,
        "weight": "FE_HOGAR",
        "wtp": [("Q42", "internet_connection_unspecified")],
        "barriers": {
            "P13_7": "equipment_cost_too_high",
            "P13_8": "fixed_service_cost_too_high",
            "P13_12": "fixed_more_expensive_than_mobile",
        },
    },
    "XI": {
        "year": 2024,
        "weight": "POND_HOGAR_FE",
        "wtp": [("Q42", "fixed_internet"), ("Q42_1", "mobile_internet_at_home")],
        "barriers": {
            "P13_7": "equipment_cost_too_high",
            "P13_8": "fixed_service_cost_too_high",
            "P13_12": "fixed_more_expensive_than_mobile",
        },
    },
    "XII": {
        "year": 2025,
        "weight": "FE_HOGAR",
        "wtp": [("Q42", "fixed_internet"), ("Q42_1", "mobile_internet_at_home")],
        "barriers": {
            "P13_7": "equipment_cost_too_high",
            "P13_8": "fixed_service_cost_too_high",
            "P13_12": "fixed_more_expensive_than_mobile",
        },
    },
}


def norm(value: object) -> str:
    text = "" if value is None else str(value)
    text = unicodedata.normalize("NFKD", text)
    return "".join(c for c in text if not unicodedata.combining(c)).strip().lower()


def clean_savs(paths):
    return [p for p in paths if p.suffix.lower() == ".sav" and not p.name.startswith("._") and "__MACOSX" not in p.parts]


def read_wave(spec, cfg, workdir):
    required = {cfg["weight"], *[v for v, _ in cfg["wtp"]], *cfg["barriers"].keys()}
    errors = []
    for sav in clean_savs(base.extract_sav_files(spec, workdir)):
        try:
            df, meta = pyreadstat.read_sav(str(sav), apply_value_formats=False, formats_as_category=False, user_missing=False)
        except Exception as exc:
            errors.append(f"{sav.name}: {exc!r}")
            continue
        if required.issubset(df.columns):
            return df, meta, sav.name
        errors.append(f"{sav.name}: missing {sorted(required - set(df.columns))}")
    raise RuntimeError("No SAV with required affordability variables: " + " | ".join(errors))


def valid_numeric(series: pd.Series, meta, variable: str) -> pd.Series:
    s = pd.to_numeric(series, errors="coerce")
    labels = (meta.variable_value_labels or {}).get(variable, {}) or {}
    invalid_codes = []
    for code, label in labels.items():
        t = norm(label)
        if any(x in t for x in ["ns/nr", "ns nr", "no sabe", "no responde", "no aplica"]):
            try:
                invalid_codes.append(float(code))
            except Exception:
                pass
    if invalid_codes:
        s = s.mask(s.isin(invalid_codes))
    # WTP is a monetary amount in CLP. Zero/non-positive and extreme placeholders are excluded.
    s = s.where((s > 0) & (s <= 500_000))
    return s


def weighted_quantile(values, weights, q):
    v = np.asarray(values, dtype=float)
    w = np.asarray(weights, dtype=float)
    mask = np.isfinite(v) & np.isfinite(w) & (w > 0)
    v, w = v[mask], w[mask]
    if len(v) == 0:
        return np.nan
    order = np.argsort(v)
    v, w = v[order], w[order]
    cumulative = np.cumsum(w)
    cutoff = q * cumulative[-1]
    return float(v[np.searchsorted(cumulative, cutoff, side="left")])


def summarize_wtp(df, meta, cfg, wave, sav_name, source_url):
    rows = []
    weights = pd.to_numeric(df[cfg["weight"]], errors="coerce")
    labels = meta.column_names_to_labels or {}
    for variable, service in cfg["wtp"]:
        values = valid_numeric(df[variable], meta, variable)
        valid = values.notna() & weights.notna() & (weights > 0)
        n = int(valid.sum())
        if n < 30:
            continue
        v = values[valid].to_numpy(dtype=float)
        w = weights[valid].to_numpy(dtype=float)
        rows.append({
            "reference_year": cfg["year"],
            "survey_wave": wave,
            "service_scope": service,
            "variable": variable,
            "question": labels.get(variable, ""),
            "n_unweighted_valid": n,
            "weighted_households_or_respondents": round(float(w.sum()), 3),
            "weighted_mean_clp": round(float(np.average(v, weights=w)), 0),
            "weighted_median_clp": round(weighted_quantile(v, w, 0.50), 0),
            "weighted_p25_clp": round(weighted_quantile(v, w, 0.25), 0),
            "weighted_p75_clp": round(weighted_quantile(v, w, 0.75), 0),
            "minimum_valid_clp": round(float(np.min(v)), 0),
            "maximum_valid_clp": round(float(np.max(v)), 0),
            "weight_variable": cfg["weight"],
            "source_url": source_url,
            "sav_file": sav_name,
            "interpretation": "maximum willingness to pay; not actual tariff or current household expenditure",
        })
    return rows


def infer_selected_code(series: pd.Series, meta, variable: str):
    vals = sorted(pd.to_numeric(series.dropna(), errors="coerce").dropna().unique().tolist())
    labels = (meta.variable_value_labels or {}).get(variable, {}) or {}
    # Prefer explicit labels when available.
    selected = []
    for code, label in labels.items():
        t = norm(label)
        if t in {"si", "sí", "seleccionado", "mencionado", "marca"} or t.startswith("si "):
            try:
                selected.append(float(code))
            except Exception:
                pass
    if len(selected) == 1:
        return selected[0], "value label"
    # Multiple-response variables in these verified P13 blocks are stored as 0/1.
    if set(vals).issubset({0.0, 1.0}) and 1.0 in vals:
        return 1.0, "binary 0/1 coding"
    raise RuntimeError(f"Cannot defensibly infer selected code for {variable}; values={vals}, labels={labels}")


def summarize_barriers(df, meta, cfg, wave, sav_name, source_url):
    rows = []
    weights = pd.to_numeric(df[cfg["weight"]], errors="coerce")
    labels = meta.column_names_to_labels or {}
    for variable, indicator in cfg["barriers"].items():
        raw = pd.to_numeric(df[variable], errors="coerce")
        selected_code, coding_note = infer_selected_code(raw, meta, variable)
        valid = raw.notna() & weights.notna() & (weights > 0)
        n = int(valid.sum())
        if n < 30:
            continue
        denom = float(weights[valid].sum())
        selected = valid & raw.eq(selected_code)
        num = float(weights[selected].sum())
        rows.append({
            "reference_year": cfg["year"],
            "survey_wave": wave,
            "indicator": indicator,
            "variable": variable,
            "question": labels.get(variable, ""),
            "n_unweighted_valid": n,
            "n_unweighted_selected": int(selected.sum()),
            "weighted_population_in_question_universe": round(denom, 3),
            "weighted_selected": round(num, 3),
            "selected_pct": round(num / denom * 100.0, 4) if denom else np.nan,
            "selected_code": selected_code,
            "coding_note": coding_note,
            "weight_variable": cfg["weight"],
            "source_url": source_url,
            "sav_file": sav_name,
            "universe_note": "households answering reasons for not having own paid fixed broadband; not all households",
        })
    return rows


def main():
    OUTDIR.mkdir(parents=True, exist_ok=True)
    wtp_rows, barrier_rows, manifest = [], [], []
    selected_specs = [s for s in base.SURVEYS if s["wave"] in WAVES]

    with tempfile.TemporaryDirectory() as td:
        workdir = Path(td)
        for spec in selected_specs:
            wave = spec["wave"]
            cfg = WAVES[wave]
            print(f"Processing affordability {wave} / {cfg['year']}")
            df, meta, sav_name = read_wave(spec, cfg, workdir)
            wtp = summarize_wtp(df, meta, cfg, wave, sav_name, spec["url"])
            barriers = summarize_barriers(df, meta, cfg, wave, sav_name, spec["url"])
            wtp_rows.extend(wtp)
            barrier_rows.extend(barriers)
            manifest.append({
                "reference_year": cfg["year"],
                "survey_wave": wave,
                "household_weight": cfg["weight"],
                "wtp_variables": " | ".join(v for v, _ in cfg["wtp"]),
                "barrier_variables": " | ".join(cfg["barriers"].keys()),
                "wtp_rows_published": len(wtp),
                "barrier_rows_published": len(barriers),
                "source_url": spec["url"],
                "sav_file": sav_name,
            })

    wtp_df = pd.DataFrame(wtp_rows).sort_values(["reference_year", "service_scope"])
    barrier_df = pd.DataFrame(barrier_rows).sort_values(["reference_year", "indicator"])
    manifest_df = pd.DataFrame(manifest).sort_values("reference_year")

    if len(wtp_df) < 5:
        raise RuntimeError(f"Expected at least five WTP summaries, got {len(wtp_df)}")
    if len(barrier_df) != 9:
        raise RuntimeError(f"Expected nine cost-barrier summaries, got {len(barrier_df)}")

    wtp_df.to_csv(OUTDIR / "subtel_willingness_to_pay_2023_2025.csv", index=False)
    barrier_df.to_csv(OUTDIR / "subtel_cost_barriers_2023_2025.csv", index=False)
    manifest_df.to_csv(OUTDIR / "affordability_mapping_manifest.csv", index=False)

    readme = """# Asequibilidad digital — evidencia SUBTEL

Esta carpeta incorpora una dimensión de asequibilidad construida directamente desde las encuestas oficiales SUBTEL 2023, 2024 y 2025.

## Qué mide

`subtel_willingness_to_pay_2023_2025.csv` resume el **máximo monto declarado que las personas/hogares estarían dispuestos a pagar** por una conexión a Internet. Se publican media, mediana y percentiles ponderados usando el factor de hogar de cada ola.

Esto **no es el precio de mercado, la tarifa contratada ni el gasto real del hogar**. Es una medida declarada de disposición máxima a pagar y debe interpretarse como evidencia de asequibilidad desde la demanda.

`subtel_cost_barriers_2023_2025.csv` mide tres razones declaradas dentro del universo de hogares que responde por qué no tiene banda ancha fija propia y pagada:

- costo del equipo o terminal demasiado alto
- costo del servicio fijo demasiado alto
- Internet fija más cara que Internet móvil

El denominador es el universo que responde el bloque P13, no el total de hogares de Chile.

## Reglas

- se usa el factor de expansión de hogares de cada encuesta
- no se almacenan microdatos SAV en GitHub
- se excluyen NS/NR y valores monetarios no positivos
- se suprimen resultados con menos de 30 observaciones válidas sin ponderar
- no se construye un índice de asequibilidad ni se divide por ingreso sin una definición longitudinal homogénea del denominador

## Comparabilidad

En 2024 y 2025 las preguntas Q42/Q42.1 distinguen Internet fija e Internet móvil en el hogar. En 2023 Q42 pregunta por un servicio de conexión a Internet sin esa misma separación; por eso se conserva como `internet_connection_unspecified` y no se fuerza a la serie fija.

Las tres barreras P13 seleccionadas mantienen una formulación suficientemente equivalente en 2023–2025 para presentarlas juntas, pero sus porcentajes describen el universo específico de no contratación de banda ancha fija.

`affordability_mapping_manifest.csv` registra variables, ponderadores, fuente y archivo SAV utilizado.

Última revisión: 2026-08-13.
"""
    (OUTDIR / "README.md").write_text(readme, encoding="utf-8")

    print("WTP summaries")
    print(wtp_df[["reference_year", "service_scope", "n_unweighted_valid", "weighted_mean_clp", "weighted_median_clp", "weighted_p25_clp", "weighted_p75_clp"]].to_string(index=False))
    print("\nCost barriers")
    print(barrier_df[["reference_year", "indicator", "n_unweighted_valid", "selected_pct", "selected_code", "coding_note"]].to_string(index=False))


if __name__ == "__main__":
    main()
