#!/usr/bin/env python3
"""Download official SUBTEL survey microdata and publish only aggregate profiles.

The script intentionally does NOT retain raw microdata in the repository. It downloads
public SPSS files from SUBTEL, extracts metadata, identifies likely expansion-factor
variables, and creates aggregate distributions with suppression of small cells.
"""

from __future__ import annotations

import argparse
import json
import re
import shutil
import tempfile
import zipfile
from pathlib import Path
from typing import Iterable

import numpy as np
import pandas as pd
import pyreadstat
import requests

SURVEYS = [
    {
        "reference_year": 2025,
        "wave": "XII",
        "label": "Duodecima Encuesta Acceso y Usos de Internet",
        "url": "https://www.subtel.gob.cl/wp-content/uploads/2026/02/BBDDSubtel2025_031225.sav_.zip",
        "archive": "zip",
    },
    {
        "reference_year": 2024,
        "wave": "XI",
        "label": "Undecima Encuesta Acceso y Usos de Internet",
        "url": "https://www.subtel.gob.cl/wp-content/uploads/2025/02/BBDD_Subtel2024_03022025.sav_.zip",
        "archive": "zip",
    },
    {
        "reference_year": 2023,
        "wave": "X",
        "label": "Decima Encuesta Acceso y Usos de Internet",
        "url": "https://www.subtel.gob.cl/wp-content/uploads/2024/05/BBDD_Acceso_y_uso_Internet_v4.sav",
        "archive": "sav",
    },
    {
        "reference_year": 2017,
        "wave": "IX",
        "label": "Novena Encuesta Acceso y Usos de Internet",
        "url": "https://www.subtel.gob.cl/wp-content/uploads/2018/07/BBDD_IX_Encuesta_VFINAL_PUB.sav",
        "archive": "sav",
    },
    {
        "reference_year": 2016,
        "wave": "VIII",
        "label": "Octava Encuesta Acceso y Usos de Internet",
        "url": "https://www.subtel.gob.cl/wp-content/uploads/2018/02/BASE_DATOS_SUBTEL_8A_ENCUESTA_ACCESO_VF.sav",
        "archive": "sav",
    },
    {
        "reference_year": 2015,
        "wave": "VII",
        "label": "Septima Encuesta Acceso y Usos de Internet - factor corregido",
        "url": "https://www.subtel.gob.cl/wp-content/uploads/2018/02/Base_septima_encuesta_Internet_factor_hogar_2016.sav",
        "archive": "sav",
    },
    {
        "reference_year": 2014,
        "wave": "VI",
        "label": "Sexta Encuesta Acceso y Usos de Internet",
        "url": "https://www.subtel.gob.cl/wp-content/uploads/2015/04/SUB_NACIONAL_ENTREVISTADO_VF_VPUBL.sav",
        "archive": "sav",
    },
    {
        "reference_year": 2013,
        "wave": "V",
        "label": "Quinta Encuesta Acceso y Usos de Internet",
        "url": "https://www.subtel.gob.cl/wp-content/uploads/2015/04/encuesta_subtel_2013_20140522_publica.sav",
        "archive": "sav",
    },
    {
        "reference_year": 2012,
        "wave": "IV",
        "label": "Cuarta Encuesta Acceso y Usos de Internet",
        "url": "https://www.subtel.gob.cl/images/stories/apoyo_articulos/estudios/base_hogares_2012.zip",
        "archive": "zip",
    },
    {
        "reference_year": 2011,
        "wave": "III",
        "label": "Tercera Encuesta Acceso y Usos de Internet",
        "url": "https://www.subtel.gob.cl/images/stories/apoyo_articulos/estudios/base_datos_final_2.zip",
        "archive": "zip",
    },
]

WEIGHT_PATTERN = re.compile(r"factor|expan|ponder|weight|peso", re.I)
FREE_TEXT_PATTERN = re.compile(r"abierta|especifique|otro cual|coment|observ", re.I)


def slugify(text: str) -> str:
    text = re.sub(r"[^0-9A-Za-z]+", "_", text).strip("_")
    return text.lower() or "dataset"


def download(url: str, path: Path) -> None:
    headers = {"User-Agent": "Chile-Digital-Inclusion research pipeline/1.0"}
    with requests.get(url, headers=headers, stream=True, timeout=120) as r:
        r.raise_for_status()
        with path.open("wb") as fh:
            for chunk in r.iter_content(chunk_size=1024 * 1024):
                if chunk:
                    fh.write(chunk)


def extract_sav_files(spec: dict, workdir: Path) -> list[Path]:
    suffix = ".zip" if spec["archive"] == "zip" else ".sav"
    source = workdir / f"source_{spec['reference_year']}_{spec['wave']}{suffix}"
    download(spec["url"], source)
    if spec["archive"] == "sav":
        return [source]

    target = workdir / f"unzipped_{spec['reference_year']}_{spec['wave']}"
    target.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(source) as zf:
        zf.extractall(target)
    savs = sorted(p for p in target.rglob("*") if p.is_file() and p.suffix.lower() == ".sav")
    if not savs:
        raise RuntimeError(f"No .sav files found in {spec['url']}")
    return savs


def safe_json(obj) -> str:
    try:
        return json.dumps(obj, ensure_ascii=False, sort_keys=True)
    except TypeError:
        return json.dumps({str(k): str(v) for k, v in (obj or {}).items()}, ensure_ascii=False)


def detect_weight_candidates(df: pd.DataFrame, labels: dict[str, str]) -> list[dict]:
    rows = []
    for col in df.columns:
        label = labels.get(col, "") or ""
        if not WEIGHT_PATTERN.search(f"{col} {label}"):
            continue
        series = pd.to_numeric(df[col], errors="coerce")
        valid = series.dropna()
        if len(valid) == 0:
            continue
        positive_share = float((valid > 0).mean())
        unique = int(valid.nunique())
        score = 0
        if "factor" in col.lower(): score += 4
        if re.search(r"expan|ponder", col, re.I): score += 4
        if re.search(r"factor|expan|ponder", label, re.I): score += 4
        if positive_share > 0.95: score += 2
        if unique > 20: score += 1
        rows.append({
            "variable": col,
            "label": label,
            "positive_share": round(positive_share, 5),
            "distinct_values": unique,
            "score": score,
        })
    return sorted(rows, key=lambda x: (-x["score"], x["variable"]))


def choose_weight(candidates: list[dict]) -> str | None:
    if not candidates:
        return None
    best = candidates[0]
    if best["score"] >= 8 and (len(candidates) == 1 or best["score"] >= candidates[1]["score"] + 2):
        return best["variable"]
    return None


def weighted_mean(values: pd.Series, weights: pd.Series) -> float | None:
    x = pd.to_numeric(values, errors="coerce")
    w = pd.to_numeric(weights, errors="coerce")
    mask = x.notna() & w.notna() & (w > 0)
    if not mask.any():
        return None
    return float(np.average(x[mask], weights=w[mask]))


def category_label(value, labels_map: dict) -> str:
    if value in labels_map:
        return str(labels_map[value])
    # SPSS numeric codes can be represented as ints/floats inconsistently.
    try:
        fv = float(value)
        for key, lbl in labels_map.items():
            try:
                if float(key) == fv:
                    return str(lbl)
            except Exception:
                pass
    except Exception:
        pass
    return str(value)


def profile_dataset(spec: dict, sav_path: Path, out: dict[str, list]) -> None:
    df, meta = pyreadstat.read_sav(
        str(sav_path),
        apply_value_formats=False,
        formats_as_category=False,
        user_missing=False,
    )
    labels = meta.column_names_to_labels or {}
    value_labels = meta.variable_value_labels or {}
    candidates = detect_weight_candidates(df, labels)
    selected_weight = choose_weight(candidates)

    dataset_id = f"{spec['reference_year']}_{spec['wave']}_{slugify(sav_path.stem)}"
    out["manifest"].append({
        "dataset_id": dataset_id,
        "reference_year": spec["reference_year"],
        "survey_wave": spec["wave"],
        "survey_label": spec["label"],
        "rows": len(df),
        "columns": len(df.columns),
        "selected_weight": selected_weight or "",
        "weight_candidates": ";".join(c["variable"] for c in candidates),
        "source_url": spec["url"],
    })
    for c in candidates:
        out["weights"].append({"dataset_id": dataset_id, **c, "selected": c["variable"] == selected_weight})

    weights = df[selected_weight] if selected_weight else None

    for col in df.columns:
        s = df[col]
        label = labels.get(col, "") or ""
        nonnull = s.dropna()
        distinct = int(nonnull.nunique(dropna=True))
        missing_pct = round(float(s.isna().mean() * 100), 4)
        lbl_map = value_labels.get(col, {}) or {}
        is_free_text = bool(FREE_TEXT_PATTERN.search(f"{col} {label}"))
        out["variables"].append({
            "dataset_id": dataset_id,
            "reference_year": spec["reference_year"],
            "survey_wave": spec["wave"],
            "variable": col,
            "label": label,
            "dtype": str(s.dtype),
            "nonmissing_n": int(s.notna().sum()),
            "distinct_values": distinct,
            "missing_pct": missing_pct,
            "has_value_labels": bool(lbl_map),
            "value_labels_json": safe_json(lbl_map),
            "is_weight_candidate": any(c["variable"] == col for c in candidates),
            "selected_weight": col == selected_weight,
            "source_url": spec["url"],
        })

        # Aggregate categorical distributions only. Small cells are suppressed.
        if 2 <= distinct <= 40 and len(nonnull) >= 100 and not is_free_text:
            counts = nonnull.value_counts(dropna=True, sort=False)
            denom = int(counts.sum())
            weighted_denom = None
            if weights is not None:
                w = pd.to_numeric(weights, errors="coerce")
                valid_weight = s.notna() & w.notna() & (w > 0)
                weighted_denom = float(w[valid_weight].sum())
            for value, n in counts.items():
                n = int(n)
                if n < 30:
                    continue
                weighted_n = None
                weighted_pct = None
                if weights is not None and weighted_denom and weighted_denom > 0:
                    w = pd.to_numeric(weights, errors="coerce")
                    mask = (s == value) & w.notna() & (w > 0)
                    weighted_n = float(w[mask].sum())
                    weighted_pct = weighted_n / weighted_denom * 100
                out["categorical"].append({
                    "dataset_id": dataset_id,
                    "reference_year": spec["reference_year"],
                    "survey_wave": spec["wave"],
                    "variable": col,
                    "variable_label": label,
                    "category_code": value,
                    "category_label": category_label(value, lbl_map),
                    "n_unweighted": n,
                    "pct_unweighted": round(n / denom * 100, 5),
                    "weighted_n": "" if weighted_n is None else round(weighted_n, 3),
                    "pct_weighted": "" if weighted_pct is None else round(weighted_pct, 5),
                    "weight_variable": selected_weight or "",
                    "cell_rule": "published only when unweighted n >= 30",
                })
        elif pd.api.types.is_numeric_dtype(s) and distinct > 40 and len(nonnull) >= 100:
            x = pd.to_numeric(s, errors="coerce").dropna()
            row = {
                "dataset_id": dataset_id,
                "reference_year": spec["reference_year"],
                "survey_wave": spec["wave"],
                "variable": col,
                "variable_label": label,
                "n_unweighted": int(x.size),
                "mean": round(float(x.mean()), 6),
                "p25": round(float(x.quantile(.25)), 6),
                "median": round(float(x.median()), 6),
                "p75": round(float(x.quantile(.75)), 6),
                "min": round(float(x.min()), 6),
                "max": round(float(x.max()), 6),
                "weighted_mean": "",
                "weight_variable": selected_weight or "",
            }
            if weights is not None:
                wm = weighted_mean(s, weights)
                if wm is not None:
                    row["weighted_mean"] = round(wm, 6)
            out["numeric"].append(row)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", default="data/subtel_microdata")
    parser.add_argument("--years", nargs="*", type=int)
    args = parser.parse_args()

    output = Path(args.output)
    if output.exists():
        shutil.rmtree(output)
    output.mkdir(parents=True, exist_ok=True)

    results = {k: [] for k in ["manifest", "weights", "variables", "categorical", "numeric", "errors"]}
    surveys = [s for s in SURVEYS if not args.years or s["reference_year"] in args.years]

    with tempfile.TemporaryDirectory() as td:
        workdir = Path(td)
        for spec in surveys:
            print(f"Processing {spec['reference_year']} {spec['wave']}...")
            try:
                savs = extract_sav_files(spec, workdir)
                for sav in savs:
                    profile_dataset(spec, sav, results)
            except Exception as exc:
                print(f"ERROR {spec['reference_year']} {spec['wave']}: {exc}")
                results["errors"].append({
                    "reference_year": spec["reference_year"],
                    "survey_wave": spec["wave"],
                    "source_url": spec["url"],
                    "error": repr(exc),
                })

    filenames = {
        "manifest": "dataset_manifest.csv",
        "weights": "weight_candidates.csv",
        "variables": "variable_dictionary.csv",
        "categorical": "categorical_distributions.csv",
        "numeric": "numeric_summary.csv",
        "errors": "processing_errors.csv",
    }
    for key, filename in filenames.items():
        pd.DataFrame(results[key]).to_csv(output / filename, index=False, encoding="utf-8")

    summary = {
        "surveys_requested": len(surveys),
        "datasets_processed": len(results["manifest"]),
        "variables_profiled": len(results["variables"]),
        "categorical_rows_published": len(results["categorical"]),
        "numeric_rows_published": len(results["numeric"]),
        "processing_errors": len(results["errors"]),
        "small_cell_rule": "categorical cells with unweighted n < 30 are not published",
        "raw_microdata_committed": False,
    }
    (output / "profile_summary.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
