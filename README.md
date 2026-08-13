# Chile Digital Inclusion

Repositorio abierto para analizar inclusión, exclusión y vulnerabilidad digital en Chile a partir de evidencia territorial y social.

El proyecto organiza indicadores provenientes de Censo 2024, CASEN 2013–2024, SUBTEL 2025 y productos públicos derivados del Atlas de la Desconexión Digital 2026. Su foco no es solo medir acceso a Internet, sino distinguir entre conexión formal, disponibilidad de dispositivos, dependencia móvil y capacidad real de uso digital.

## Preguntas de investigación

- ¿Dónde se concentra la desconexión digital en Chile?
- ¿Qué territorios presentan mayor severidad y cuáles concentran mayor volumen de hogares afectados?
- ¿Qué tan extendida está la dependencia exclusiva o predominante del teléfono móvil?
- ¿Dónde la falta de computador limita usos educativos, laborales y administrativos?
- ¿Cómo se cruza la brecha digital con ruralidad, envejecimiento, discapacidad, ingreso y género?

## Fuentes principales

- Censo de Población y Vivienda 2024 — INE
- CASEN — Ministerio de Desarrollo Social y Familia
- SUBTEL — estadísticas y microdatos de conectividad y dispositivos
- Ookla Open Data — calidad de servicio cuando corresponde
- Elaboración propia a partir de bases públicas consolidadas

## Estructura

```text
Chile-Digital-Inclusion/
├── README.md
├── LICENSE
├── CITATION.cff
├── data/
│   ├── national_snapshot_2026.csv
│   ├── regional_disconnect_snapshot.csv
│   ├── commune_cases_public.csv
│   └── data_sources.csv
├── docs/
│   ├── methodology.md
│   ├── data_dictionary.md
│   └── key_findings.md
└── scripts/
    └── build_summary.py
```

## Principios de publicación

El repositorio mantiene una frontera clara entre evidencia pública y trabajo metodológico propietario. No publica el Índice de Vulnerabilidad Digital completo, ponderadores internos, modelos comerciales ni bases privadas. Los indicadores derivados incluidos aquí son agregados, trazables y adecuados para uso público.

## Autor

Sebastian Elgueta Godoy

Sociología, políticas públicas, telecomunicaciones e infraestructura digital.

## Licencia

Código bajo licencia MIT. Las fuentes de terceros mantienen sus condiciones originales de uso.
