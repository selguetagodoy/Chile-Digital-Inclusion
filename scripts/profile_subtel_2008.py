#!/usr/bin/env python3
"""Profile the official 2008 SUBTEL SPSS archive without committing microdata."""

from __future__ import annotations

import json
import subprocess
import tempfile
from pathlib import Path

import pandas as pd
import pyreadstat
import requests

URL = "https://www.subtel.gob.cl/images/stories/articles/subtel/asocfile/base_completa_270409_spss.rar"
OUT = Path("data/subtel_2008")


def read_sav_robust(path: Path):
    errors = []
    for enc in [None, "latin1", "windows-1252"]:
        try:
            kwargs = dict(apply_value_formats=False, formats_as_category=False, user_missing=False)
            if enc:
                kwargs["encoding"] = enc
            return pyreadstat.read_sav(str(path), **kwargs), enc or "auto"
        except Exception as exc:
            errors.append(f"{enc or 'auto'}: {exc!r}")
    raise RuntimeError(" | ".join(errors))


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    manifest, variables, cats, nums, errors = [], [], [], [], []
    with tempfile.TemporaryDirectory() as td:
        td = Path(td)
        rar = td / "subtel_2008.rar"
        r = requests.get(URL, headers={"User-Agent": "Chile-Digital-Inclusion/1.0"}, timeout=120)
        r.raise_for_status()
        rar.write_bytes(r.content)
        extract = td / "extract"
        extract.mkdir()
        subprocess.run(["7z", "x", str(rar), f"-o{extract}", "-y"], check=True)
        savs = [p for p in extract.rglob("*") if p.is_file() and p.suffix.lower() == ".sav" and not p.name.startswith("._")]
        for sav in savs:
            try:
                (df, meta), enc = read_sav_robust(sav)
                dataset_id = "2008_I_" + sav.stem.lower().replace(" ", "_")
                labels = meta.column_names_to_labels or {}
                value_labels = meta.variable_value_labels or {}
                manifest.append({"dataset_id":dataset_id,"reference_year":2008,"survey_wave":"I","rows":len(df),"columns":len(df.columns),"encoding":enc,"source_url":URL})
                for col in df.columns:
                    s = df[col]
                    non = s.dropna()
                    distinct = int(non.nunique())
                    label = labels.get(col, "") or ""
                    variables.append({"dataset_id":dataset_id,"variable":col,"label":label,"dtype":str(s.dtype),"nonmissing_n":int(s.notna().sum()),"distinct_values":distinct,"missing_pct":round(float(s.isna().mean()*100),4),"value_labels_json":json.dumps(value_labels.get(col,{}) or {}, ensure_ascii=False)})
                    if 2 <= distinct <= 40 and len(non) >= 100:
                        counts = non.value_counts(sort=False)
                        denom = int(counts.sum())
                        for val,n in counts.items():
                            n=int(n)
                            if n < 30: continue
                            lbl = (value_labels.get(col,{}) or {}).get(val, str(val))
                            cats.append({"dataset_id":dataset_id,"variable":col,"variable_label":label,"category_code":val,"category_label":lbl,"n_unweighted":n,"pct_unweighted":round(n/denom*100,5),"cell_rule":"n >= 30"})
                    elif pd.api.types.is_numeric_dtype(s) and distinct > 40 and len(non) >= 100:
                        x=pd.to_numeric(s, errors='coerce').dropna()
                        nums.append({"dataset_id":dataset_id,"variable":col,"variable_label":label,"n_unweighted":int(x.size),"mean":round(float(x.mean()),6),"median":round(float(x.median()),6),"min":round(float(x.min()),6),"max":round(float(x.max()),6)})
            except Exception as exc:
                errors.append({"file":sav.name,"error":repr(exc)})
    pd.DataFrame(manifest).to_csv(OUT/"dataset_manifest.csv",index=False)
    pd.DataFrame(variables).to_csv(OUT/"variable_dictionary.csv",index=False)
    pd.DataFrame(cats).to_csv(OUT/"categorical_distributions.csv",index=False)
    pd.DataFrame(nums).to_csv(OUT/"numeric_summary.csv",index=False)
    pd.DataFrame(errors).to_csv(OUT/"processing_errors.csv",index=False)
    summary={"datasets_processed":len(manifest),"variables_profiled":len(variables),"categorical_rows":len(cats),"numeric_rows":len(nums),"errors":len(errors),"raw_microdata_committed":False}
    (OUT/"summary.json").write_text(json.dumps(summary,indent=2)+"\n")
    print(json.dumps(summary,indent=2))

if __name__ == "__main__":
    main()
