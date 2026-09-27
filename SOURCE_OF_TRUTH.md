# SOURCE OF TRUTH

This file defines the canonical evidence hierarchy for **Chile Digital Inclusion**.

## Canonical analytical layers

1. Public data products under `data/`, generated or integrated through repository scripts.
2. Data dictionaries and methodology under `docs/`.
3. `data/source_registry.csv` for source identity and analytical role.
4. `config/source_watch.csv` plus `docs/source_watch.md` for monitored publication endpoints and source-change detection.
5. `data/metadata/release_manifest.csv` and validation outputs for release-level control.
6. README and public site content as explanatory surfaces, not primary evidence.

## Source-change rule

The existing official-source watcher is the canonical monitoring mechanism. A detected change never updates analytical data automatically. It only triggers review. New values must be checked against publication date, statistical reference period, universe, methodology, unit, precision and compatibility with existing vintages before promotion.

## Integrity rules

- Do not interpolate or extrapolate missing observations.
- Do not backcast or silently overwrite historical vintages.
- Keep household access, administrative infrastructure, network presence and observed performance as distinct evidence families.
- Preserve original precision and qualifiers.
- Treat source and method changes as explicit breaks when comparability is not guaranteed.
- Derived layers must remain reproducible from documented upstream inputs.

## Citation

Use `CITATION.cff` for project citation and attribute each third-party source according to its own terms.
