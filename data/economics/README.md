# Economía del sector de telecomunicaciones — estados financieros y márgenes (2024–2026)

**Corte de investigación: 29 de octubre de 2026.** Tabla curada: [telecom_financials_2024_2026.csv](telecom_financials_2024_2026.csv).

Esta capa añade economía de operadores al observatorio: ingresos, EBITDA, margen EBITDA, CAPEX, EBIT, utilidad neta y razón de endeudamiento **cuando la fuente reporta el indicador**. La unidad de todas las cifras monetarias del CSV es **millones de pesos chilenos corrientes (CLP MM)**. Valores vacíos significan **no comprobado en la fuente utilizada**, no cero. Todas las observaciones numéricas están marcadas como `actual`, salvo que se indique lo contrario; el conjunto no incluye proyecciones.

## Política de unidad y comparación

La clave analítica es `company + scope + period`. `period_start`, `period_end` y `period_kind` identifican si la cifra representa un trimestre autónomo (Q1, Q2, Q3), primer semestre acumulado (H1), nueve meses acumulados (9M) o año completo (FY). **No sumar un trimestre a un período acumulado que lo contenga.**

Los valores se publican según el **perímetro económico reportado**, que nunca se confunde con una licencia, marca, filial o participación de conexiones de SUBTEL:

| Entidad | `scope` | Restricción |
| --- | --- | --- |
| Entel | `chile_operations` | Resultados del negocio Chile según reporte de Entel; no incluye Perú |
| GTD | `group_consolidated` | Grupo con operaciones en Chile y otros países; no es EBITDA solo Chile |
| GTD | `chile_revenue_segment` | Solo ingresos del segmento Chile; EBITDA, CAPEX y margen chilenos quedan vacíos |
| WOM | `chile_operations` | EBITDA **ajustado** publicado por la empresa; no equiparar con EBITDA IFRS |
| América Móvil / ClaroVTR | `southern_cone_segment` | Incluye Chile, Paraguay y Uruguay; no atribuir ingresos o EBITDA completos a ClaroVTR Chile |
| Mundo | `chile_business_rating_adjusted` | EBITDA histórico **ajustado por S&P Global Ratings**, no idéntico al de otros operadores |

Para GTD, la compañía define EBITDA como resultado operacional más depreciaciones, amortizaciones y castigos de activos/materiales, **sin incluir IFRS 15 ni IFRS 16**, según su análisis razonado. El campo `ebitda_basis` conserva estas diferencias. En Mundo, 2024a y 2025a son datos **históricos ajustados por la clasificadora**; no se incluyen estimaciones 2026e en la serie de hechos observados.

## Diccionario resumido

- `revenue_clp_mm`: ingresos totales según **la definición de la propia fuente**, no un agregado reconstruido; puede incorporar otras partidas de ingreso o ventas de terminales.
- `ebitda_clp_mm`: EBITDA reportado según `ebitda_basis`, con ajustes identificados en ese campo.
- `ebitda_margin_pct`: margen reportado en % (no re-calculado con falsa precisión). Control de proximidad: `100 * EBITDA / ingresos`, tolerancia 0,25 puntos por redondeos.
- `capex_clp_mm`: gasto de inversión según definición de la fuente. En GTD corresponde a compras de PPE más intangibles; no sustituir por flujo neto de inversión.
- `ebit_clp_mm`: resultado operacional antes de intereses e impuestos. Puede ser negativo.
- `net_income_clp_mm`: utilidad o pérdida del ejercicio; vacío cuando no hay desglose atribuible al perímetro.
- `reported_leverage_ratio_x`: razón de apalancamiento reportada. **No es una métrica homogeneizada**: GTD publica deuda financiera neta/EBITDA (2,54x a junio de 2026); S&P para Mundo publica deuda/EBITDA ajustado (4,1x en 2025); nunca comparar sin leer su definición.
- `source_class`, `source_url`, `source_published`: tipo, enlace directo y fecha de divulgación cuando fue verificable.
- `status`: `actual` para resultados históricos. Las estimaciones de terceros no se publican como resultados observados.
- `notes`: restricciones de interpretación y redondeos.

## Fuentes verificadas

1. **Entel**, presentación de resultados 2T y 1S 2026, 3 agosto 2026. Tabla «Chile: Financial Results and Operating Figures», p. 9 (cifras CLP MM, incluidas columnas comparativas 2025): https://entel.cdn.modyo.com/uploads/99eb3169-3586-45fb-9b91-a047d4d4248b/original/Press_Release_2Q26.pdf
2. **GTD Grupo Teleductos**, Análisis Razonado al 30 de junio de 2026, pp. 2–7. Tabla consolidada con comparativo 2025, desagregación de ingresos Chile, inversiones y endeudamiento: https://www.gtd.cl/documents/1600005/0/Ana%CC%81lisis_razonado_94727000_202606.pdf
3. **WOM**, comunicado oficial de resultados 1T2026 (25 mayo 2026): https://sobrenosotros.wom.cl/wom-logra-crecimiento-en-ingresos-totales-y-mantiene-un-solido-2do-lugar-en-conexiones-moviles/
4. **WOM**, comunicado de 2T2026 reproducido por DPL News (21 agosto 2026). Fuente de segunda publicación; resultados reportados por WOM: https://dplnews.com/wom-continua-crecimiento-en-ingresos-totales-y-ebitda-respaldado-por-una-sana-posicion-financiera/
5. **WOM**, resultados anuales 2025 publicados en Diario Financiero (24 marzo 2026). Cifras redondeadas comunicadas por la empresa: https://www.df.cl/empresas/telecom-tecnologia/wom-concluye-el-2025-con-timida-alza-de-2-1-en-sus-ingresos-totales-pero
6. **América Móvil**, Reporte financiero y operativo 3T2026, emitido el 20 octubre de 2026 en **Bolsa Mexicana de Valores**, sección Cono Sur, con comparativos 3T2025/9M2025: https://www.bmv.com.mx/docs-pub/eventemi/eventemi_1596486_1.pdf
7. **S&P Global Ratings**, nota de asignación de calificación de DB Terra Chile Holdco SpA (8 abril 2026), cuadro histórico 2024a–2025a: https://www.spglobal.com/ratings/en/regulatory/article/-/view/type/HTML/id/3542457

**Brecha pendiente (sin completar con supuestos):** resultados consolidados de Telefónica Chile y Telefónica Móviles Chile en el ejercicio 2026, tras el cambio de control de Telefónica Móviles Chile en febrero de 2026. Las razones sociales, el período y el perímetro deben verificarse contra la CMF o EEFF del emisor antes de incorporarlos. La falta de un dato de un operador no significa que su EBITDA sea cero ni que sea comparable con el EBITDA de otro grupo.

## Relación con las demás capas del repositorio

Las series SUBTEL de conexiones y tráfico se miden por operador y servicio; Ookla mide tests de red; el Censo mide hogares. Los financieros tienen **grano operador/grupo × período × perímetro**. No se replican en las 346 comunas, no se suman para formar «ingresos totales del mercado chileno» y no se imputan a cada hogar. La comparación correcta exige unidad geográfica, razón social, tecnología y ventana temporal compatibles.

Un análisis económico posterior puede estimar indicadores como CAPEX/ingresos o ingresos por conexión **solo cuando la definición temporal, empresa y denominador estén armonizados**. No se deben producir automáticamente ARPU sintéticos a partir de ingresos consolidados y conexiones SUBTEL.

## QA y mantenimiento

Cada fila conserva fuente directa, fechas, alcance, base EBITDA y notas. Ejecutar `python scripts/validate_telecom_financials.py` para verificar claves únicas, períodos, campos numéricos, márgenes y URLs. Una revisión de la web corporativa o una noticia nueva **no altera automáticamente el CSV**: registrar nuevos valores solo tras cotejo de la fuente, de su definición, período y alcance. Recalcular luego el manifiesto del repositorio mediante el workflow de metadatos existente.
