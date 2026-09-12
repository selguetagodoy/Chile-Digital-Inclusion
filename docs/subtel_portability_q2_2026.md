# SUBTEL — Portabilidad Numérica Q2 2026

Esta capa incorpora los indicadores oficiales publicados por SUBTEL el 6 de agosto de 2026 para el segundo trimestre de 2026, correspondiente a abril, mayo y junio.

Fuente primaria: https://www.subtel.gob.cl/informe-de-portabilidad-de-subtel-mas-de-753-mil-numeros-moviles-y-fijos-cambiaron-de-compania-durante-el-segundo-trimestre-de-2026/

## Productos

- `data/subtel_portability_2026/portability_summary_q2_2026.csv` conserva los totales trimestrales y acumulados, junto con las participaciones móvil/fija publicadas por SUBTEL.
- `data/subtel_portability_2026/mobile_operator_net_q2_2026.csv` conserva la variación neta por empresa móvil exactamente con las etiquetas y valores publicados.
- `data/subtel_portability_2026/qa_q2_2026.csv` registra controles aritméticos y discrepancias no resueltas.

## Valores principales

Durante Q2 2026 se registraron 753.930 portaciones: 742.719 móviles y 11.211 fijas. Al 30 de junio de 2026 el sistema acumulaba 44.096.038 portaciones, de las cuales 42.255.681 eran móviles y 1.840.357 fijas.

SUBTEL publicó para el segmento móvil las siguientes variaciones netas trimestrales: Claro +70.106; Mundo +5.998; Wom +1.602; OPS +110; GTD Móvil +47; VTR -43; Virgin -551; Simple -654; Entel -23.704; Movistar -53.438.

## Regla de interpretación

La portabilidad mide cambios de proveedor y dinámica competitiva. No es una medida de cobertura, calidad, acceso efectivo, penetración, satisfacción ni inclusión digital.

Los saldos netos por operador publicados en la página suman -527. El repositorio no corrige, redistribuye ni fuerza ese residual a cero. Se mantiene como `not_reconciled` hasta que una fuente oficial entregue una explicación o una tabla más completa.

La mención periodística de una caída de 2% respecto de 2025 no se incorpora como serie estructurada porque la página no identifica con suficiente precisión el valor base utilizado para esa comparación.

## Trazabilidad

- `source_id`: `subtel_portability_2026q2`
- fecha de publicación: 2026-08-06
- fecha de recuperación: 2026-09-12
- unidad estadística principal: evento de portación
- frecuencia del corte: trimestral

No se construyen tasas adicionales, promedios ni estimaciones a partir de esta publicación.
