# Inteligencia estratégica telecom Chile · 2026

**Última curaduría:** 29 de octubre de 2026. Evidencia para investigación y comunicación pública **no comercial**, incluido LinkedIn. Conservar enlaces, autoría y condiciones de reutilización de cada fuente.

## Datos agregados

| Producto | Grano | Alcance |
|---|---|---|
| [operator_market_traffic_bridge_2025_2026.csv](operator_market_traffic_bridge_2025_2026.csv) | operador × segmento (10 filas) | Internet fijo y móvil: conexiones, participación, tráfico mensual, variaciones 2025–2026 y GB por conexión |
| [coquimbo_resilience_ookla_q3_2026.csv](coquimbo_resilience_ookla_q3_2026.csv) | comuna (6 filas) | Observaciones de interrupción al 12-08-2026 vinculadas con Ookla Q2/Q3 y datos comunales Censo/SUBTEL |
| [official_strategic_events_2026.csv](official_strategic_events_2026.csv) | evento/indicador (14 filas) | Regulación de redes privadas, pilotos, inversión pública FDT, resiliencia, seguridad física y cumplimiento |
| [qa_summary.csv](qa_summary.csv) | control | Verificación de filas, unicidad, cuotas y períodos |

## Metodología

### 1. Puente entre conexiones y tráfico
Fuentes: [panel anual junio internet móvil](../subtel_sector_series/annual_june_mobile_operator_panel.csv) y [panel anual junio internet fijo](../subtel_sector_series/annual_june_fixed_operator_panel.csv). Datos administrativos SUBTEL para junio 2025 y junio 2026.

* `net_adds_yoy = connections_2026_06 - connections_2025_06`.
* `connections_yoy_pct = 100 × (connections_2026_06 / connections_2025_06 - 1)`.
* `share_delta_pp = share_2026_pct - share_2025_pct` (puntos porcentuales).
* `traffic_yoy_pct = 100 × (traffic_2026_tb / traffic_2025_tb - 1)`.
* `gb_per_connection = monthly_traffic_tb × 1.000 / end_of_month_connections`. Conversión decimal; **es un cociente agregado aproximado**, no consumo de individuos, ni métrica financiera ARPU, margen, COGS o costo por GB.
* `traffic_share_minus_connection_share_pp = traffic_share_2026_pct - share_2026_pct`. Descriptivo de la intensidad relativa de uso.

La nomenclatura por operador sigue las series SUBTEL; «Grupo Claro-VTR» agrupa marcas según origen administrativo. No confundir conexiones móviles de internet 3G–5G con total de abonados de telefonía móvil. Los datos no comparan rentabilidad ni cobertura de red.

### 2. Cruce comunal Coquimbo
Fuentes: [Maestro comunal integrado](../communal_master/chile_digital_inclusion_communes_2026_integrated.csv) y [observaciones SUBTEL de resiliencia](../network_resilience_2026/network_resilience_observations_2026.csv). Unión por comuna y región **Coquimbo**; seis comunas sin duplicados.

* La columna de antenas fuera de servicio es una **fotografía oficial del 12 de agosto**, durante recuperación de la emergencia.
* Las velocidades Ookla son medias ponderadas de tests de un trimestre completo (julio a septiembre).
* Las conexiones fijas por 100 hogares usan SUBTEL junio 2026 / hogares Censo 2024; son intensidad de conexiones, no porcentaje de cobertura.
* El indicador exploratorio `joint_low_fixed_and_mobile_flag=yes` exige **≥100 tests móviles Q3**, **menos de 30 conexiones fijas residenciales por 100 hogares** y **descarga móvil Q3 inferior a 75 Mbps**.
* Coincidencia territorial **no prueba** que la emergencia causó la velocidad trimestral, ni que representa disponibilidad anual. No inferir pérdidas, operadores culpables ni volumen de usuarios afectados.

### 3. Registro de acontecimientos verificables
Solo observaciones con enlaces oficiales directos a SUBTEL, y unidad, fecha, calificador y estatus explícitos. Un registro puede corresponder a un aspecto diferente de un mismo proyecto.

* Espectro privado industrial: la banda pasó de **2.300–2.340** a **2.300–2.360 MHz**. Total actual **60 MHz**; incremento **20 MHz**. No contabilizar la totalidad como nueva asignación.
* Acuerdo SUBTEL–OnLab apoyado por Corfo: oportunidad de pilotos industriales, **no** ingresos B2B, contratos comerciales o cifra de mercado.
* Aysén: adjudicación FDT no equivale a fibra instalada; las 7.802 viviendas potenciales no son clientes ya conectados; el monto de subsidio no equivale a EBITDA.
* Cobro ordenado de garantías FON no equivale a recaudación efectivamente verificada.
* Robos de baterías y vandalismo: estadísticas sectoriales reportadas por SUBTEL con atribución a ChileTelcos; no estimar pérdidas financieras por compañía.
* Plan Nacional Digital: ejes presentados para diálogo, no plan final aprobado al corte.

## Límites y buenas prácticas para publicaciones

**Cortes diferentes:** Ookla hasta septiembre 2026; conexiones y tráfico SUBTEL hasta junio; portabilidad Q2; resultados financieros según perímetro y última publicación. Mantener período, unidad, universo y fuente al lado de cada gráfico.

**Calidad frente a continuidad:** Speedtest mide rendimiento donde hubo tests; el snapshot de caída de antenas mide continuidad durante emergencia. No convertirlos en un mismo indicador de calidad habitual.

**Finanzas:** para ingresos/EBITDA/CAPEX utilizar [capa económica](../economics/README.md) que conserva empresa, período, geografía, base contable, ajustes y fuentes. No comparar WOM ajustado, Entel Chile y América Móvil Cono Sur como si fueran el mismo universo. No construir ARPU sintético con ingresos consolidados.

**Licencias:** Ookla Open Data está bajo CC BY-NC-SA 4.0; el uso descrito es divulgación pública no comercial. La publicación no comercial **no elimina** atribución, indicación de cambios, ni exigencias de compartir derivados bajo condiciones de la licencia cuando sean aplicables. [Fuente y licencia](https://github.com/teamookla/ookla-open-data). Mantener los avisos y demás derechos correspondientes de otras fuentes.

**Estado:** estos productos derivan de un snapshot fijo y no se actualizan automáticamente con cada publicación de la fuente. Para nuevas cifras hay que rehacer los cruces, auditar la metodología y ajustar los períodos.

## Fuentes primarias de acontecimientos
- [Normativa y redes privadas 5G](https://www.subtel.gob.cl/subtel-anuncia-pionera-ampliacion-de-espectro-para-el-desarrollo-de-redes-privadas-5g-y-futuras-generaciones-moviles/)
- [SUBTEL–OnLab–Corfo](https://www.subtel.gob.cl/subtel-y-onlab-suscriben-acuerdo-para-impulsar-el-5g-y-6g-en-los-sectores-productivos-con-el-apoyo-de-corfo/)
- [Mesa de seguridad de Valparaíso](https://www.subtel.gob.cl/subtel-realiza-1o-mesa-de-conectividad-y-seguridad-publica-en-valparaiso-region-es-la-que-posee-mas-robos-de-baterias-en-chile/)
- [Fiscalización Coquimbo](https://www.subtel.gob.cl/coquimbo-subtel-revela-resultados-de-fiscalizaciones-y-confirma-descuentos-de-hasta-100-en-comunas-afectadas-por-el-temporal/)
- [Última Milla Aysén](https://www.subtel.gob.cl/ministerio-de-transportes-y-telecomunicaciones-y-gobierno-regional-de-aysen-anuncian-la-adjudicacion-del-proyecto-fibra-optica-ultima-milla-que-conectara-33-localidades-rurales-con-alta-velocidad/)
- [Garantías FON](https://www.subtel.gob.cl/subsecretaria-de-telecomunicaciones-ordena-cobro-integro-de-garantias-a-wom-por-incumplimientos-en-fibra-optica-nacional-fon/)
- [Plan Nacional Digital](https://www.subtel.gob.cl/subtel-presenta-ejes-del-plan-nacional-digital-para-fomentar-la-inversion-apagar-el-3g-y-preparar-el-camino-al-6g/)
- [Oficio preventivo del 20 de octubre](https://www.subtel.gob.cl/por-sistema-frontal-subtel-oficia-a-empresas-de-telecomunicaciones-para-reforzar-la-conectividad-ante-emergencias/)
