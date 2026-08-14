# SUBTEL 2025 digital skills by age

## Purpose

This layer makes the age gradient in selected digital skills directly usable for analysis of the second-level digital divide. It combines two public tables already present in the repository:

- `data/subtel_2025_digital_skills_basic.csv`
- `data/subtel_2025_digital_skills_intermediate.csv`

The canonical derived table is:

- `data/subtel_longitudinal/subtel_digital_skills_by_age_2025.csv`

## Statistical unit and scope

The rows reproduce published age-group percentages from the XII SUBTEL Internet Access and Use Survey (2025). The age groups available in the source tables are 16–29, 30–44, 45–59 and 60–74 years.

No value is created for people aged 75 or more because the source tables used here do not publish a separate 75+ row. Missing age groups are not imputed.

## Skills included

Basic/productivity items:

- word processor
- spreadsheet
- presentation software

Intermediate/configuration items:

- transfer files
- connect router or printer
- install/configure applications

## Comparison rule

For each skill, the derived table reports the percentage-point difference relative to the 30–44 age group. The 30–44 group is used as the descriptive reference because the companion CASEN age analysis in this repository also uses it as an adult benchmark.

The gaps are arithmetic differences only. They are not regression coefficients and should not be interpreted as causal age effects.

## Main descriptive result

For the six selected skills, the 60–74 age group is between 44.9 and 50.7 percentage points below the 30–44 group. This provides direct age-stratified evidence of a second-level digital divide in 2025, rather than relying only on a national 16+ skills average.

## Limits

- The layer is cross-sectional for 2025.
- It does not provide a separate 75+ skills estimate.
- It does not include design-based confidence intervals in the public derived table.
- It does not control for education, income, sex, territory, household structure or prior technological experience.
- The percentages remain self-reported ability/use measures and are not performance tests.

These limits should be kept separate from the stronger claim now supported by the data: age-specific differences in selected digital skills are directly observed for 60–74 versus younger groups.
