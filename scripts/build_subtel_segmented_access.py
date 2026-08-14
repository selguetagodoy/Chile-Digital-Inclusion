#!/usr/bin/env python3
"""Build harmonized SUBTEL household-access profiles by region, zone and socioeconomic group.

The pipeline downloads official public SAV files temporarily, applies each wave's household
expansion factor, and publishes only aggregates. It does not commit raw microdata.

Scope is deliberately conservative: 2015, 2016, 2017, 2023, 2024 and 2025. These are the
waves used by the curated access series. Region and urban/rural mappings are explicit.
Socioeconomic segmentation is included only when an explicit quintile/GSE-like categorical
variable with <=10 categories can be verified in the source dictionary.
"""

from __future__ import annotations

import re
import tempfile
import unicodedata
from pathlib import Path

import numpy as np
import pandas as pd
import pyreadstat

import profile_subtel_microdata as base

OUTDIR = Path("data/subtel_segments")

WAVES = {
    "XII": {"year": 2025, "access": "P1", "region": "COD_REGION", "zone": "ZONA", "weight": "FE_HOGAR", "expected_pct": 96.6},
    "XI": {"year": 2024, "access": "P1", "region": "COD_REGION", "zone": "ZONA", "weight": "POND_HOGAR_FE", "expected_pct": 96.5},
    "X": {"year": 2023, "access": "P1", "region": "COD_REGION", "zone": "ZONA", "weight": "FE_HOGAR", "expected_pct": 94.3},
    "IX": {"year": 2017, "access": "P5", "region": "REGION", "zone": "ZONA", "weight": "FACTOR_HOGAR", "expected_pct": 87.4, "socioeconomic": "QUINTIL_PCD"},
    "VIII": {"year": 2016, "access": "P5", "region": "regionfinal", "zone": "zona_cod", "weight": "FACT_HOGAR", "expected_pct": 79.3, "socioeconomic": "Quintil_final"},
    "VII": {"year": 2015, "access": "P5", "region": "region", "zone": "zona", "weight": "factor_hogar_2016", "expected_pct": 70.2, "socioeconomic": "Quintil"},
}


def norm(value: object) -> str:
    text = "" if value is None else str(value)
    text = unicodedata.normalize("NFKD", text)
    text = "".join(c for c in text if not unicodedata.combining(c))
    return re.sub(r"\s+", " ", text).strip().lower()


def clean_savs(paths: list[Path]) -> list[Path]:
    return [p for p in paths if p.suffix.lower() == ".sav" and not p.name.startswith("._") and "__MACOSX" not in p.parts]


def read_matching_sav(spec: dict, workdir: Path, access_var: str):
    errors = []
    for sav in clean_savs(base.extract_sav_files(spec, workdir)):
        try:
            df, meta = pyreadstat.read_sav(str(sav), apply_value_formats=False, formats_as_category=False, user_missing=False)
            if access_var in df.columns:
                return df, meta, sav.name
            errors.append(f"{sav.name}: missing {access_var}")
        except Exception as exc:
            errors.append(f"{sav.name}: {exc!r}")
    raise RuntimeError("No matching SAV: " + " | ".join(errors))


def value_label_map(meta, variable: str) -> dict:
    return (meta.variable_value_labels or {}).get(variable, {}) or {}


def label_for(meta, variable: str, value: object) -> str:
    labels = value_label_map(meta, variable)
    if value in labels:
        return str(labels[value])
    # pyreadstat may use integer keys while pandas stores floats.
    try:
        iv = int(float(value))
        if iv in labels:
            return str(labels[iv])
    except Exception:
        pass
    return str(value)


def detect_yes_value(meta, variable: str, series: pd.Series):
    labels = value_label_map(meta, variable)
    candidates = []
    for code, label in labels.items():
        t = norm(label)
        if t in {"si", "sí"} or t.startswith("si ") or t.startswith("si,"):
            candidates.append(code)
    if len(candidates) == 1:
        return candidates[0]
    # Conservative fallback for the verified binary access variables.
    vals = sorted(v for v in series.dropna().unique())
    if len(vals) == 2 and 1 in vals:
        return 1
    raise RuntimeError(f"Could not identify unique YES category for {variable}; labels={labels}")


def weighted_access(df: pd.DataFrame, access_var: str, weight_var: str, yes_value, mask: pd.Series):
    access = df[access_var]
    weights = pd.to_numeric(df[weight_var], errors="coerce")
    valid = mask & access.notna() & weights.notna() & (weights > 0)
    n_unweighted = int(valid.sum())
    if n_unweighted < 30:
        return None
    denom = float(weights[valid].sum())
    yes = valid & access.eq(yes_value)
    num = float(weights[yes].sum())
    return {
        "n_unweighted": n_unweighted,
        "weighted_households": round(denom, 3),
        "weighted_households_with_paid_access": round(num, 3),
        "paid_access_pct": round(num / denom * 100.0, 4) if denom else np.nan,
    }


def find_socioeconomic(df: pd.DataFrame, meta, preferred: str | None) -> tuple[str | None, str]:
    if preferred and preferred in df.columns:
        return preferred, "explicit wave mapping"

    labels = meta.column_names_to_labels or {}
    exact_names = {"gse", "gse_final", "nse", "nse_final", "quintil", "quintil_final", "quintil_pcd"}
    candidates = []
    for col in df.columns:
        distinct = int(df[col].dropna().nunique())
        if not (2 <= distinct <= 10):
            continue
        name = norm(col).replace(" ", "_")
        lab = norm(labels.get(col, ""))
        score = 0
        if name in exact_names:
            score += 10
        if "quintil" in name or "quintil" in lab:
            score += 6
        if re.search(r"\bgse\b|grupo socioeconomico|nivel socioeconomico", f"{name} {lab}"):
            score += 5
        if score:
            candidates.append((score, col, distinct, lab))
    if not candidates:
        return None, "no explicit <=10-category quintile/GSE variable verified"
    candidates.sort(key=lambda x: (-x[0], x[2], x[1]))
    best = candidates[0]
    return best[1], f"dictionary-detected explicit socioeconomic category ({best[2]} categories)"


def segment_rows(df, meta, cfg, wave, source_url, sav_name):
    access_var = cfg["access"]
    weight_var = cfg["weight"]
    for required in (access_var, weight_var, cfg["region"], cfg["zone"]):
        if required not in df.columns:
            raise RuntimeError(f"{wave}: required variable {required} not found")

    yes = detect_yes_value(meta, access_var, df[access_var])
    rows = []

    national = weighted_access(df, access_var, weight_var, yes, pd.Series(True, index=df.index))
    if national:
        rows.append({
            "reference_year": cfg["year"], "survey_wave": wave, "segment_dimension": "national",
            "segment_variable": "", "segment_code": "ALL", "segment_label": "Chile",
            **national, "household_weight": weight_var, "access_variable": access_var,
            "access_yes_code": yes, "source_url": source_url, "sav_file": sav_name,
        })

    for dimension, variable in (("region", cfg["region"]), ("urban_rural", cfg["zone"])):
        for value in sorted(df[variable].dropna().unique(), key=lambda x: str(x)):
            result = weighted_access(df, access_var, weight_var, yes, df[variable].eq(value))
            if not result:
                continue
            rows.append({
                "reference_year": cfg["year"], "survey_wave": wave, "segment_dimension": dimension,
                "segment_variable": variable, "segment_code": value, "segment_label": label_for(meta, variable, value),
                **result, "household_weight": weight_var, "access_variable": access_var,
                "access_yes_code": yes, "source_url": source_url, "sav_file": sav_name,
            })

    socio_var, socio_note = find_socioeconomic(df, meta, cfg.get("socioeconomic"))
    if socio_var:
        for value in sorted(df[socio_var].dropna().unique(), key=lambda x: str(x)):
            result = weighted_access(df, access_var, weight_var, yes, df[socio_var].eq(value))
            if not result:
                continue
            rows.append({
                "reference_year": cfg["year"], "survey_wave": wave, "segment_dimension": "socioeconomic",
                "segment_variable": socio_var, "segment_code": value, "segment_label": label_for(meta, socio_var, value),
                **result, "household_weight": weight_var, "access_variable": access_var,
                "access_yes_code": yes, "source_url": source_url, "sav_file": sav_name,
            })

    meta_row = {
        "reference_year": cfg["year"], "survey_wave": wave, "access_variable": access_var,
        "region_variable": cfg["region"], "zone_variable": cfg["zone"], "socioeconomic_variable": socio_var or "",
        "socioeconomic_selection_note": socio_note, "household_weight": weight_var,
        "yes_code": yes, "national_paid_access_pct": national["paid_access_pct"] if national else np.nan,
        "published_reference_pct": cfg["expected_pct"],
        "difference_pp_vs_published": round((national["paid_access_pct"] - cfg["expected_pct"]), 4) if national else np.nan,
        "source_url": source_url, "sav_file": sav_name,
    }
    return rows, meta_row


def main():
    OUTDIR.mkdir(parents=True, exist_ok=True)
    all_rows, manifest, errors = [], [], []
    selected_specs = [s for s in base.SURVEYS if s["wave"] in WAVES]

    with tempfile.TemporaryDirectory() as td:
        workdir = Path(td)
        for spec in selected_specs:
            wave = spec["wave"]
            cfg = WAVES[wave]
            print(f"Processing {wave} / {cfg['year']}")
            try:
                df, meta, sav_name = read_matching_sav(spec, workdir, cfg["access"])
                rows, meta_row = segment_rows(df, meta, cfg, wave, spec["url"], sav_name)
                all_rows.extend(rows)
                manifest.append(meta_row)
            except Exception as exc:
                errors.append({"reference_year": cfg["year"], "survey_wave": wave, "error": repr(exc), "source_url": spec["url"]})

    out = pd.DataFrame(all_rows)
    manifest_df = pd.DataFrame(manifest).sort_values("reference_year")
    errors_df = pd.DataFrame(errors, columns=["reference_year", "survey_wave", "error", "source_url"])

    if len(manifest_df) != len(WAVES):
        raise RuntimeError(f"Expected {len(WAVES)} waves; processed {len(manifest_df)}. Errors: {errors}")

    # Sanity check against SUBTEL's published harmonized national access series.
    if (manifest_df["difference_pp_vs_published"].abs() > 1.25).any():
        bad = manifest_df.loc[manifest_df["difference_pp_vs_published"].abs() > 1.25]
        raise RuntimeError("National weighted estimates differ materially from published series:\n" + bad.to_string(index=False))

    out = out.sort_values(["reference_year", "segment_dimension", "segment_code"], key=lambda s: s.astype(str)).reset_index(drop=True)
    out.to_csv(OUTDIR / "household_paid_access_by_segment_2015_2025.csv", index=False)
    out[out["segment_dimension"] == "region"].to_csv(OUTDIR / "household_paid_access_by_region_2015_2025.csv", index=False)
    out[out["segment_dimension"] == "urban_rural"].to_csv(OUTDIR / "household_paid_access_by_urban_rural_2015_2025.csv", index=False)
    out[out["segment_dimension"] == "socioeconomic"].to_csv(OUTDIR / "household_paid_access_by_socioeconomic_group_2015_2025.csv", index=False)
    manifest_df.to_csv(OUTDIR / "segment_mapping_manifest.csv", index=False)
    errors_df.to_csv(OUTDIR / "processing_errors.csv", index=False)

    readme = """# SUBTEL — acceso segmentado\n\nEsta carpeta publica tabulados ponderados de acceso propio y pagado a Internet en el hogar para las olas 2015, 2016, 2017, 2023, 2024 y 2025.\n\n## Productos\n\n- `household_paid_access_by_segment_2015_2025.csv` — maestro largo de segmentos.\n- `household_paid_access_by_region_2015_2025.csv` — acceso por región.\n- `household_paid_access_by_urban_rural_2015_2025.csv` — acceso urbano/rural.\n- `household_paid_access_by_socioeconomic_group_2015_2025.csv` — quintil/GSE cuando existe una categoría explícita y verificable.\n- `segment_mapping_manifest.csv` — variables y ponderadores usados en cada ola, junto con control contra la cifra nacional publicada.\n\n## Regla metodológica\n\nSe usa exclusivamente el factor de expansión de hogares correspondiente a cada encuesta. Las celdas con menos de 30 observaciones sin ponderar no se publican. El nivel socioeconómico no se reconstruye a partir de ingresos: entra solo si la base contiene una variable explícita de quintil o GSE con hasta diez categorías.\n\nLas categorías se mantienen tal como vienen etiquetadas en cada ola. Esto permite análisis por año, pero no implica que las categorías socioeconómicas sean idénticas entre encuestas.\n\nLos SAV oficiales se descargan durante GitHub Actions y no se almacenan en el repositorio.\n\nÚltima revisión: 2026-08-13.\n"""
    (OUTDIR / "README.md").write_text(readme, encoding="utf-8")

    print(f"Published {len(out)} segment rows across {len(manifest_df)} waves")
    print(manifest_df[["reference_year", "survey_wave", "national_paid_access_pct", "published_reference_pct", "difference_pp_vs_published", "socioeconomic_variable"]].to_string(index=False))


if __name__ == "__main__":
    main()
