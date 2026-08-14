#!/usr/bin/env python3
"""Build a machine-readable dictionary for the integrated communal master."""

from __future__ import annotations

from pathlib import Path
import re
import pandas as pd

MASTER = Path("data/communal_master/chile_digital_inclusion_communes_2026_integrated.csv")
OUT_CSV = Path("data/metadata/communal_master_dictionary.csv")
OUT_MD = Path("docs/communal_master_dictionary.md")

BASE = {
    "region": ("Código de región", "Censo/Atlas", "territorio", "código", "Identificador numérico de región."),
    "region_nombre": ("Región", "Censo/Atlas", "territorio", "texto", "Nombre de la región."),
    "provincia": ("Código de provincia", "Censo/Atlas", "territorio", "código", "Identificador numérico de provincia."),
    "provincia_nombre": ("Provincia", "Censo/Atlas", "territorio", "texto", "Nombre de la provincia."),
    "comuna": ("Código de comuna", "Censo/Atlas", "territorio", "código", "Código territorial usado como llave principal del maestro."),
    "comuna_nombre": ("Comuna", "Censo/Atlas", "territorio", "texto", "Nombre de la comuna."),
    "hogares_total": ("Hogares totales", "Censo/Atlas", "hogar", "número", "Total de hogares de la comuna en la capa integrada."),
    "hogares_validos_internet": ("Hogares válidos para Internet", "Censo/Atlas", "hogar", "número", "Hogares con respuesta válida para la variable de acceso a Internet."),
    "hogares_sin_internet_n": ("Hogares sin Internet", "Censo/Atlas", "hogar", "número", "Número de hogares clasificados sin acceso a Internet."),
    "hogares_sin_internet_pct": ("Hogares sin Internet", "Censo/Atlas", "hogar", "porcentaje", "Porcentaje de hogares válidos para Internet clasificados sin acceso."),
    "hogares_trampa_movil_n": ("Hogares con dependencia móvil", "Atlas derivado", "hogar", "número", "Proxy operacional de hogares con conectividad dependiente del móvil. No es una categoría oficial del Censo."),
    "hogares_trampa_movil_pct": ("Dependencia móvil", "Atlas derivado", "hogar", "porcentaje", "Proxy operacional de dependencia móvil. No es una categoría oficial del Censo."),
    "hogares_con_tel_movil_n": ("Hogares con teléfono móvil", "Censo/Atlas", "hogar", "número", "Hogares con disponibilidad de teléfono móvil."),
    "hogares_con_tel_movil_pct": ("Hogares con teléfono móvil", "Censo/Atlas", "hogar", "porcentaje", "Porcentaje de hogares con teléfono móvil."),
    "hogares_con_computador_n": ("Hogares con computador", "Censo/Atlas", "hogar", "número", "Hogares con computador."),
    "hogares_con_computador_pct": ("Hogares con computador", "Censo/Atlas", "hogar", "porcentaje", "Porcentaje de hogares con computador."),
    "hogares_con_internet_fija_n": ("Hogares con Internet fija", "Censo/Atlas", "hogar", "número", "Hogares con Internet fija."),
    "hogares_con_internet_fija_pct": ("Internet fija", "Censo/Atlas", "hogar", "porcentaje", "Porcentaje de hogares con Internet fija."),
    "hogares_con_internet_movil_n": ("Hogares con Internet móvil", "Censo/Atlas", "hogar", "número", "Hogares con Internet móvil."),
    "hogares_con_internet_movil_pct": ("Internet móvil", "Censo/Atlas", "hogar", "porcentaje", "Porcentaje de hogares con Internet móvil."),
    "hogares_con_internet_satelital_n": ("Hogares con Internet satelital", "Censo/Atlas", "hogar", "número", "Hogares con Internet satelital."),
    "hogares_con_internet_satelital_pct": ("Internet satelital", "Censo/Atlas", "hogar", "porcentaje", "Porcentaje de hogares con Internet satelital."),
    "hogares_urbanos_n": ("Hogares urbanos", "Censo/Atlas", "hogar", "número", "Número de hogares urbanos."),
    "hogares_urbanos_pct": ("Hogares urbanos", "Censo/Atlas", "hogar", "porcentaje", "Porcentaje de hogares urbanos."),
    "hogares_rurales_n": ("Hogares rurales", "Censo/Atlas", "hogar", "número", "Número de hogares rurales."),
    "hogares_rurales_pct": ("Hogares rurales", "Censo/Atlas", "hogar", "porcentaje", "Porcentaje de hogares rurales."),
    "pct_hacinamiento": ("Hacinamiento", "Censo/Atlas", "hogar", "porcentaje", "Porcentaje de hogares con hacinamiento según la capa integrada."),
    "pct_hacinamiento_critico": ("Hacinamiento crítico", "Censo/Atlas", "hogar", "porcentaje", "Porcentaje de hogares con hacinamiento crítico."),
    "pct_no_propietario": ("Hogares no propietarios", "Censo/Atlas", "hogar", "porcentaje", "Porcentaje de hogares cuya vivienda no es propia."),
    "pct_arrendatario": ("Hogares arrendatarios", "Censo/Atlas", "hogar", "porcentaje", "Porcentaje de hogares arrendatarios."),
    "pct_tenencia_irregular": ("Tenencia irregular", "Censo/Atlas", "hogar", "porcentaje", "Porcentaje de hogares con condición de tenencia irregular en la capa integrada."),
    "pct_monoparental": ("Hogares monoparentales", "Censo/Atlas", "hogar", "porcentaje", "Porcentaje de hogares monoparentales."),
    "pct_hogares_con_nna": ("Hogares con NNA", "Censo/Atlas", "hogar", "porcentaje", "Porcentaje de hogares con niños, niñas o adolescentes."),
    "pct_hogares_con_mayores": ("Hogares con personas mayores", "Censo/Atlas", "hogar", "porcentaje", "Porcentaje de hogares con personas mayores."),
    "pct_hogares_con_discapacidad": ("Hogares con discapacidad", "Censo/Atlas", "hogar", "porcentaje", "Porcentaje de hogares con al menos una persona con discapacidad en la capa integrada."),
    "pct_jefatura_femenina": ("Jefatura femenina", "Censo/Atlas", "hogar", "porcentaje", "Porcentaje de hogares con jefatura femenina."),
    "pct_hogares_multigeneracionales": ("Hogares multigeneracionales", "Censo/Atlas", "hogar", "porcentaje", "Porcentaje de hogares multigeneracionales."),
    "macrozona_operativa": ("Macrozona operativa", "Atlas derivado", "territorio", "categoría", "Agrupación territorial descriptiva usada por el proyecto."),
    "ookla_observed_any_2026q1": ("Observación Ookla disponible", "Ookla Open Data", "test de red", "sí/no", "Indica si la comuna tiene observaciones fijas o móviles asignadas en Q1 2026."),
    "ookla_period": ("Período Ookla", "Ookla Open Data", "test de red", "trimestre", "Período de referencia de las métricas Ookla integradas."),
    "ookla_spatial_method": ("Método espacial Ookla", "Ookla Open Data", "test de red", "texto", "Regla espacial usada para asignar tiles a comunas."),
}


def ookla_meta(col: str):
    m = re.match(r"ookla_(fixed|mobile)_(.+)", col)
    if not m:
        return None
    net, metric = m.groups()
    net_es = "fija" if net == "fixed" else "móvil"
    source = "Ookla Open Data"
    unit = "número"
    description = f"Métrica de red {net_es} agregada desde tiles Ookla."
    label = f"Ookla {net_es} {metric}"
    if "download_mbps" in metric:
        unit, label = "Mbps", f"Descarga Ookla {net_es}"
        description = f"Velocidad media de descarga de red {net_es}, ponderada por número de tests del tile."
    elif "upload_mbps" in metric:
        unit, label = "Mbps", f"Carga Ookla {net_es}"
        description = f"Velocidad media de carga de red {net_es}, ponderada por número de tests del tile."
    elif "latency_ms" in metric and "delta" not in metric:
        unit, label = "ms", f"Latencia Ookla {net_es}"
        description = f"Latencia media de red {net_es}, ponderada por número de tests del tile."
    elif "loaded_latency" in metric:
        unit, label = "ms", f"Latencia cargada Ookla {net_es}"
    elif "delta_pct" in metric:
        unit, label = "porcentaje", f"Variación trimestral Ookla {net_es}"
        description = f"Variación porcentual Q4 2025 a Q1 2026 para red {net_es}."
    elif "tests" in metric:
        unit, label = "número", f"Tests Ookla {net_es}"
        description = f"Número de tests representados en los tiles asignados a la comuna para red {net_es}."
    elif "devices" in metric:
        unit, label = "número", f"Dispositivos Ookla {net_es}"
        description = "Suma de dispositivos reportados por tile. Puede contar un dispositivo en más de un tile y no representa usuarios únicos comunales."
    elif "tiles" in metric:
        unit, label = "número", f"Tiles Ookla {net_es}"
        description = f"Número de tiles Ookla asignados espacialmente a la comuna para red {net_es}."
    return (label, source, "test de red", unit, description)


def denominator(col: str) -> str:
    if col == "hogares_sin_internet_pct":
        return "hogares_validos_internet"
    if col.endswith("_pct") or col.startswith("pct_"):
        return "hogares_total o universo específico de la variable"
    if col.startswith("ookla_"):
        return "tests del tile cuando corresponde a promedio ponderado"
    return "no aplica"


def note(col: str) -> str:
    if "trampa_movil" in col:
        return "Proxy del proyecto; no es categoría oficial censal."
    if col.startswith("ookla_"):
        return "Ookla observa tests realizados; no equivale a cobertura universal ni a una muestra probabilística de hogares."
    return "Variable agregada; revisar metodología de la capa de origen antes de comparar universos."


def main() -> None:
    df = pd.read_csv(MASTER, nrows=5)
    rows = []
    for col in df.columns:
        meta = BASE.get(col) or ookla_meta(col)
        if meta is None:
            meta = (col.replace("_", " ").title(), "Censo/Atlas derivado", "hogar/territorio", "según variable", "Campo de la capa comunal integrada; ver documentación de origen.")
        label, source, stat_unit, unit, description = meta
        rows.append({
            "variable": col,
            "label_es": label,
            "source_layer": source,
            "statistical_unit": stat_unit,
            "territorial_level": "comuna",
            "unit": unit,
            "denominator_or_weight": denominator(col),
            "description": description,
            "comparability_note": note(col),
        })

    out = pd.DataFrame(rows)
    OUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    out.to_csv(OUT_CSV, index=False)

    source_counts = out["source_layer"].value_counts().to_dict()
    text = [
        "# Diccionario del maestro comunal integrado",
        "",
        f"El archivo documenta **{len(out)} variables** del maestro `chile_digital_inclusion_communes_2026_integrated.csv`.",
        "",
        "La tabla canónica y legible por máquinas está en `data/metadata/communal_master_dictionary.csv`.",
        "",
        "## Principios",
        "",
        "- una fila del maestro representa una comuna",
        "- los porcentajes censales se mantienen separados de métricas de desempeño de red",
        "- Ookla se interpreta como desempeño observado donde existieron tests, no como cobertura probabilística",
        "- la dependencia móvil es una proxy operacional del proyecto y no una categoría oficial del Censo",
        "- no se publican ponderadores, scores ni el Índice de Vulnerabilidad Digital completo",
        "",
        "## Variables por capa",
        "",
    ]
    for source, count in source_counts.items():
        text.append(f"- {source}: {count}")
    text += [
        "",
        "## Uso",
        "",
        "Antes de construir rankings o modelos, revisar `statistical_unit`, `denominator_or_weight` y `comparability_note`. No deben mezclarse mecánicamente hogares censales, personas ponderadas de encuesta y tests de red.",
        "",
        "Última revisión: 2026-08-13.",
    ]
    OUT_MD.write_text("\n".join(text) + "\n", encoding="utf-8")
    print(f"Wrote {len(out)} dictionary rows")


if __name__ == "__main__":
    main()
