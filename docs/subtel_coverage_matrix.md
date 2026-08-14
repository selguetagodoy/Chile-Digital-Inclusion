# Cobertura de datos SUBTEL

Este repositorio no considera completa una ola solo porque exista un resumen nacional. La cobertura se evalúa por dimensión, desagregación y comparabilidad.

## Estado actual

| Dimensión | 2015 | 2016 | 2017 | 2023 | 2024 | 2025 | Estado |
|---|---|---|---|---|---|---|---|
| Acceso pagado del hogar | Sí | Sí | Sí | Sí | Sí | Sí | Armonizado |
| Fijo / móvil / fijo+móvil | Sí | Sí | Sí | Sí | Sí | Sí | Armonizado |
| Urbano / rural | Sí | Sí | Sí | Sí | Sí | Sí | Armonizado con notas |
| Dispositivos del hogar | Sí | Sí | Sí | Sí | Sí | Sí | Armonizado con cambios de categorías |
| Frecuencia de uso | Sí | Sí | Parcial | Sí | Sí | Sí | Quiebre de ventana desde 2024 |
| Hogares solo de personas mayores | No | No | Sí | Sí | Sí | Sí | Serie descriptiva |
| Habilidades digitales | No | No | No | Sí | Sí | Sí | Serie comparable reciente |
| Habilidades por edad | No | No | No | No | No | Sí | Disponible 2025 |
| Teletrabajo por edad | No | No | No | No | No | Sí | Disponible 2025 |
| E-learning por edad | No | No | No | No | No | Sí | Disponible 2025 |
| Postulación laboral online | No | No | No | No | No | Sí | Disponible 2025 |
| Estado digital por sexo | No | No | No | No | No | Sí | Disponible 2025 |
| Seguridad digital | No | No | No | No | No | Sí | Parcial 2025 |
| IA | No aplica | No aplica | No aplica | No | Sí | Sí | Ítem introducido en 2024 |
| Jefatura de hogar por sexo | No | No | No | Sí | Pendiente | Pendiente | Parcial |
| Motivos para tener Internet | Parcial | Pendiente | Pendiente | Parcial | Pendiente | Pendiente | Requiere extracción por ola |
| Motivos para no tener Internet | Pendiente | Pendiente | Pendiente | Pendiente | Parcial | Pendiente | Requiere armonización |
| Nivel socioeconómico | Pendiente | Pendiente | Pendiente | Pendiente | Pendiente | Pendiente | Requiere extracción de bases |
| Región | Pendiente | Pendiente | Pendiente | Pendiente | Pendiente | Pendiente | Requiere extracción de bases |
| Pueblos originarios | Módulo especial | Pendiente | Pendiente | Pendiente | Pendiente | Pendiente | No mezclar con serie nacional |
| Personas mayores — usos detallados | Módulo especial | Pendiente | Pendiente | Pendiente | Pendiente | Sí | Parcial |
| Calidad o satisfacción percibida | Pendiente | Pendiente | Pendiente | Pendiente | Pendiente | Pendiente | Requiere extracción |
| Privacidad / fraude / protección | Pendiente | Pendiente | Pendiente | Pendiente | Pendiente | Parcial | Requiere extracción |

## Qué falta para una base realmente completa

La siguiente etapa debe procesar las bases de datos oficiales de cada encuesta —preferentemente los archivos SAV disponibles en SUBTEL— y generar tabulados agregados reproducibles. El objetivo no es subir microdatos sino producir matrices consistentes por año.

Prioridades de extracción:

1. `año × zona × acceso × tipo de conexión`
2. `año × sexo/jefatura × acceso y uso`
3. `año × GSE × acceso, dispositivos y usos`
4. `año × edad × acceso, dispositivos, habilidades y usos`
5. `año × región × acceso y tipo de conexión`
6. motivos de adopción y no adopción
7. seguridad, privacidad y percepción de riesgo
8. trámites, banca, educación, empleo y teletrabajo
9. módulos especiales de personas mayores y pueblos originarios
10. diccionario de preguntas y códigos para identificar quiebres de cuestionario

## Regla de publicación

Las bases oficiales pueden utilizarse para reproducir tabulados, pero el repositorio prioriza resultados agregados y trazables. Una variable solo entra en una serie longitudinal cuando su pregunta, universo y categorías son suficientemente comparables. Cuando no lo son, se publica como observación de una ola específica.

Última revisión: 2026-08-13.
