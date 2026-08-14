#!/usr/bin/env python3
"""Build weighted aggregate profiles from official SUBTEL survey microdata.

This script downloads the same public SAV files used by profile_subtel_microdata.py,
but calculates both household-weighted and person-weighted distributions where the
relevant expansion factors are available. Raw records are never committed.
"""

from __future__ import annotations

import json
import tempfile
from pathlib import Path

import numpy as np
import pandas as pd
import pyreadstat

import profile_subtel_microdata as base

# Explicit map after inspecting the official SAV dictionaries.
# When both weights are supplied, the published table contains both estimates so the
# analyst can select the one matching the question's statistical universe.
WEIGHT_MAP = {
    "XII": {"household": "FE_HOGAR", "person": "FE_PERSONAS"},
    "XI": {"household": "POND_HOGAR_FE", "person": "PON_PER_SIN_GSE_FE"},
    "X": {"household": "FE_HOGAR", "person": "FE_USO"},
    "IX": {"household": "FACTOR_HOGAR", "person": "FACTOR_PERSONA"},
    "VIII": {"household": "FACT_HOGAR", "person": "FACT_PER"},
    "VII": {"household": "factor_hogar_2016", "person": "FACT_PER"},
    "VI": {"household": "FACTOR", "person": "FACTOR"},
    "V": {"household": "fact_hog", "person": "fact_selec"},
    "IV": {"household": None, "person": None},
    "III": {"household": "Factor_Transv", "person": "Factor_Transv"},
}


def clean_sav_paths(paths):
    return [
        p for p in paths
        if not p.name.startswith("._")
        and "__MACOSX" not in p.parts
        and p.suffix.lower() == ".sav"
    ]


def weighted_total(mask: pd.Series, weights: pd.Series) -> float | None:
    w = pd.to_numeric(weights, errors="coerce")
    valid = mask & w.notna() & (w > 0)
    if not valid.any():
        return None
    return float(w[valid].sum())


def weighted_mean(values: pd.Series, weights: pd.Series) -> float | None:
    x = pd.to_numeric(values, errors="coerce")
    w = pd.to_numeric(weights, errors="coerce")
    mask = x.notna() & w.notna() & (w > 0)
    if not mask.any():
        return None
    return float(np.average(x[mask], weights=w[mask]))


def profile(spec: dict, sav_path: Path, categorical: list[dict], numeric: list[dict], manifest: list[dict]):
    df, meta = pyreadstat.read_sav(
        str(sav_path), apply_value_formats=False, formats_as_category=False, user_missing=False
    )
    labels = meta.column_names_to_labels or {}
    value_labels = meta.variable_value_labels or {}
    dataset_id = f"{spec['reference_year']}_{spec['wave']}_{base.slugify(sav_path.stem)}"

    configured = WEIGHT_MAP.get(spec["wave"], {})
    household_var = configured.get("household")
    person_var = configured.get("person")
    if household_var not in df.columns:
        household_var = None
    if person_var not in df.columns:
        person_var = None
    household_w = df[household_var] if household_var else None
    person_w = df[person_var] if person_var else None

    manifest.append({
        "dataset_id": dataset_id,
        "reference_year": spec["reference_year"],
        "survey_wave": spec["wave"],
        "rows": len(df),
        "columns": len(df.columns),
        "household_weight": household_var or "",
        "person_weight": person_var or "",
        "source_url": spec["url"],
    })

    for col in df.columns:
        s = df[col]
        label = labels.get(col, "") or ""
        nonnull = s.dropna()
        distinct = int(nonnull.nunique(dropna=True))
        is_free_text = bool(base.FREE_TEXT_PATTERN.search(f"{col} {label}"))
        lbl_map = value_labels.get(col, {}) or {}

        if 2 <= distinct <= 40 and len(nonnull) >= 100 and not is_free_text:
            counts = nonnull.value_counts(dropna=True, sort=False)
            denom = int(counts.sum())
            hh_denom = weighted_total(s.notna(), household_w) if household_w is not None else None
            pp_denom = weighted_total(s.notna(), person_w) if person_w is not None else None

            for value, n in counts.items():
                n = int(n)
                if n < 30:
                    continue
                category_mask = s.eq(value)
                hh_n = weighted_total(category_mask, household_w) if household_w is not None else None
                pp_n = weighted_total(category_mask, person_w) if person_w is not None else None
                categorical.append({
                    "dataset_id": dataset_id,
                    "reference_year": spec["reference_year"],
                    "survey_wave": spec["wave"],
                    "variable": col,
                    "variable_label": label,
                    "category_code": value,
                    "category_label": base.category_label(value, lbl_map),
                    "n_unweighted": n,
                    "pct_unweighted": round(n / denom * 100, 5),
                    "household_weight": household_var or "",
                    "household_weighted_n": "" if hh_n is None else round(hh_n, 3),
                    "household_weighted_pct": "" if hh_n is None or not hh_denom else round(hh_n / hh_denom * 100, 5),
                    "person_weight": person_var or "",
                    "person_weighted_n": "" if pp_n is None else round(pp_n, 3),
                    "person_weighted_pct": "" if pp_n is None or not pp_denom else round(pp_n / pp_denom * 100, 5),
                    "cell_rule": "published only when unweighted n >= 30",
                })

        elif pd.api.types.is_numeric_dtype(s) and distinct > 40 and len(nonnull) >= 100:
            x = pd.to_numeric(s, errors="coerce").dropna()
            numeric.append({
                "dataset_id": dataset_id,
                "reference_year": spec["reference_year"],
                "survey_wave": spec["wave"],
                "variable": col,
                "variable_label": label,
                "n_unweighted": int(x.size),
                "mean_unweighted": round(float(x.mean()), 6),
                "household_weight": household_var or "",
                "mean_household_weighted": "" if household_w is None else round(weighted_mean(s, household_w), 6),
                "person_weight": person_var or "",
                "mean_person_weighted": "" if person_w is None else round(weighted_mean(s, person_w), 6),
                "p25": round(float(x.quantile(.25)), 6),
                "median": round(float(x.median()), 6),
                "p75": round(float(x.quantile(.75)), 6),
                "min": round(float(x.min()), 6),
                "max": round(float(x.max()), 6),
            })


def main():
    outdir = Path("data/subtel_weighted")
    outdir.mkdir(parents=True, exist_ok=True)
    categorical, numeric, manifest, errors = [], [], [], []

    with tempfile.TemporaryDirectory() as td:
        workdir = Path(td)
        for spec in base.SURVEYS:
            print(f"Processing weighted profiles for {spec['wave']} / {spec['reference_year']}")
            try:
                savs = clean_sav_paths(base.extract_sav_files(spec, workdir))
                for sav in savs:
                    try:
                        profile(spec, sav, categorical, numeric, manifest)
                    except Exception as exc:
                        errors.append({
                            "reference_year": spec["reference_year"],
                            "survey_wave": spec["wave"],
                            "sav_file": sav.name,
                            "error": repr(exc),
                        })
            except Exception as exc:
                errors.append({
                    "reference_year": spec["reference_year"],
                    "survey_wave": spec["wave"],
                    "sav_file": "",
                    "error": repr(exc),
                })

    pd.DataFrame(manifest).to_csv(outdir / "dataset_manifest.csv", index=False)
    pd.DataFrame(categorical).to_csv(outdir / "categorical_weighted.csv", index=False)
    pd.DataFrame(numeric).to_csv(outdir / "numeric_weighted.csv", index=False)
    pd.DataFrame(errors).to_csv(outdir / "processing_errors.csv", index=False)

    weight_rows = []
    for wave, mapping in WEIGHT_MAP.items():
        weight_rows.append({"survey_wave": wave, **mapping})
    pd.DataFrame(weight_rows).to_csv(outdir / "weight_map.csv", index=False)

    summary = {
        "datasets_processed": len(manifest),
        "categorical_rows": len(categorical),
        "numeric_rows": len(numeric),
        "processing_errors": len(errors),
        "raw_microdata_committed": False,
        "cell_suppression": "unweighted n < 30",
        "note": "Both household and person weights are published where available; use the weight matching the questionnaire universe.",
    }
    (outdir / "summary.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n")
    print(json.dumps(summary, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
