# SUBTEL 2025 digital skills by age

## Purpose

This layer makes the published age gradient in selected digital skills directly usable for analysis of the second-level digital divide.

Canonical table:

- `data/subtel_longitudinal/subtel_digital_skills_by_age_2025.csv`

Primary source:

- SUBTEL, *Duodécima Encuesta sobre acceso, usos y usuarios de Internet en Chile*, presentation, page 82.
- https://www.subtel.gob.cl/wp-content/uploads/2026/02/Presentacion-Subtel-Acceso-y-Uso-Internet-2025_v1.pdf

## Statistical unit and scope

The results refer to people aged 16 or more in the use section of the XII SUBTEL survey. The official presentation publishes four age groups: 16–29, 30–44, 45–59 and **60 or more**.

The canonical table reproduces those published groups exactly. It must not relabel the last group as 60–74. A separate 75+ skills estimate is not published on page 82 and is not imputed.

## Skills included

Selected productivity and configuration tasks:

- word processor
- spreadsheet formulas
- presentation software
- transfer files
- connect router or printer
- install/configure applications

## Comparison rule

For each skill, the table reports the percentage-point difference relative to the 30–44 age group. This is an arithmetic descriptive comparison, not a regression coefficient or a causal age effect.

## Main descriptive result

Across the six selected tasks, the published 60+ group is between **44.6 and 50.2 percentage points** below the 30–44 group. The age gradient is therefore directly observable in SUBTEL 2025 and does not need to be inferred from the national 16+ skills average.

Examples:

- word processor: 74.0% at 30–44 versus 23.8% at 60+ (−50.2 pp)
- spreadsheet formulas: 64.6% versus 19.2% (−45.4 pp)
- transfer files: 69.1% versus 19.1% (−50.0 pp)
- install/configure applications: 63.9% versus 19.3% (−44.6 pp)

## Reconciliation note

Two earlier root-level convenience tables in the repository use a custom `60-74` label and slightly different percentages. They are not used as the canonical published-age source for the article. For claims described as published SUBTEL age-group results, use this longitudinal canonical table and the official page-82 values above.

## Remaining limits

- The age-specific layer is cross-sectional for 2025.
- SUBTEL publishes 60+ as one group, so it does not isolate 75+ in the public presentation used here.
- The public derived table does not contain design-based confidence intervals.
- The descriptive gaps do not control for education, income, sex, territory, household structure or prior technological experience.
- The measures are self-reported abilities rather than performance tests.

These limits do not negate the stronger claim supported by the published evidence: selected digital skills differ sharply by age in 2025, including a direct comparison between 60+ and younger adult groups.
