#!/usr/bin/env python3
"""Classify SUBTEL survey variables into harmonization domains using labels/names."""

from __future__ import annotations

import re
from pathlib import Path
import pandas as pd

INPUT = Path("data/subtel_microdata/variable_dictionary.csv")
OUTPUT = Path("data/subtel_microdata/harmonization_candidates.csv")

DOMAINS = {
    "geography_region": [r"\bregion\b", r"regi[oó]n"],
    "geography_urban_rural": [r"urbano", r"rural", r"zona", r"[aá]rea"],
    "geography_commune": [r"comuna"],
    "demographic_age": [r"\bedad\b", r"tramo.*edad", r"grupo.*etario", r"a[nñ]os"],
    "demographic_sex_gender": [r"\bsexo\b", r"g[eé]nero", r"hombre", r"mujer"],
    "demographic_education": [r"educaci[oó]n", r"nivel.*educ", r"estudios", r"escolaridad"],
    "demographic_income_gse": [r"ingreso", r"quintil", r"decil", r"\bgse\b", r"socioecon"],
    "demographic_employment": [r"ocupaci[oó]n", r"empleo", r"trabaj", r"actividad.*econ"],
    "household_access": [r"acceso.*internet", r"internet.*hogar", r"hogar.*internet", r"conexi[oó]n.*internet"],
    "fixed_mobile_mode": [r"internet fijo", r"internet m[oó]vil", r"banda ancha", r"solo m[oó]vil", r"tipo.*conexi[oó]n"],
    "internet_use_frequency": [r"frecuencia.*internet", r"uso.*internet", r"usa.*internet", r"utiliza.*internet", r"diariamente", r"todos los d[ií]as"],
    "devices": [r"smartphone", r"tel[eé]fono.*m[oó]vil", r"computador", r"notebook", r"laptop", r"tablet", r"televisor", r"smart.?tv", r"consola"],
    "barriers_non_access": [r"raz[oó]n.*no", r"motivo.*no", r"por qu[eé].*no", r"no.*internet", r"costo", r"caro", r"cobertura", r"no sabe.*usar"],
    "digital_skills": [r"habilidad", r"sabe.*usar", r"puede.*realizar", r"word", r"excel", r"procesador.*texto", r"planilla", r"instalar.*app", r"configurar", r"inteligencia artificial"],
    "digital_government": [r"tr[aá]mite", r"gobierno", r"estado", r"certificado", r"beneficio", r"formulario", r"consulta.*reclamo"],
    "banking_payments": [r"banco", r"bancari", r"pago", r"transferencia", r"compra.*internet", r"comercio.*electr"],
    "education_learning": [r"educaci[oó]n", r"aprendizaje", r"curso", r"e.?learning", r"estudi", r"tarea"],
    "work_telework": [r"teletrab", r"trabajo.*internet", r"buscar.*trabajo", r"postul.*laboral", r"empleo"],
    "social_communication": [r"redes sociales", r"whatsapp", r"facebook", r"instagram", r"videollamada", r"comunicar"],
    "security_privacy": [r"seguridad", r"privacidad", r"contrase", r"estafa", r"fraude", r"virus", r"proteg", r"amenaza"],
    "older_people": [r"adulto.*mayor", r"persona.*mayor", r"tercera edad", r"65.*m[aá]s", r"60.*m[aá]s"],
    "disability": [r"discapacidad", r"dificultad.*permanente", r"limitaci[oó]n"],
    "indigenous": [r"pueblo.*originario", r"ind[ií]gena", r"mapuche", r"aymara", r"rapa nui"],
    "quality_satisfaction": [r"calidad", r"velocidad", r"satisfacci[oó]n", r"problema.*servicio", r"se[nñ]al"],
}


def score(text: str, patterns: list[str]) -> int:
    return sum(1 for p in patterns if re.search(p, text, flags=re.I))


def main() -> None:
    df = pd.read_csv(INPUT, dtype=str).fillna("")
    rows = []
    for _, r in df.iterrows():
        text = f"{r['variable']} {r['label']}".lower()
        if r.get("is_weight_candidate", "").lower() == "true":
            continue
        for domain, patterns in DOMAINS.items():
            s = score(text, patterns)
            if s:
                rows.append({
                    "dataset_id": r["dataset_id"],
                    "reference_year": r["reference_year"],
                    "survey_wave": r["survey_wave"],
                    "domain": domain,
                    "score": s,
                    "variable": r["variable"],
                    "label": r["label"],
                    "nonmissing_n": r["nonmissing_n"],
                    "distinct_values": r["distinct_values"],
                    "missing_pct": r["missing_pct"],
                    "has_value_labels": r["has_value_labels"],
                })

    out = pd.DataFrame(rows)
    if not out.empty:
        out = out.sort_values(
            ["reference_year", "survey_wave", "domain", "score", "nonmissing_n"],
            ascending=[False, True, True, False, False],
        )
    out.to_csv(OUTPUT, index=False, encoding="utf-8")

    coverage = (
        out.groupby(["reference_year", "survey_wave", "domain"], dropna=False)
        .size().rename("candidate_variables").reset_index()
        if not out.empty else pd.DataFrame()
    )
    coverage.to_csv(OUTPUT.with_name("harmonization_domain_coverage.csv"), index=False, encoding="utf-8")
    print(f"candidate rows: {len(out)}")
    print(f"domain coverage rows: {len(coverage)}")


if __name__ == "__main__":
    main()
