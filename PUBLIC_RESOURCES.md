# Public resources

This index lists the public resources declared in [`datapackage.json`](datapackage.json). It is intentionally narrower than the full repository tree.

**Project:** Chile Digital Inclusion  
**Working package version:** 0.1.0  
**Canonical landing:** https://selguetagodoy.github.io/dataset-chile-digital-inclusion.html  
**Archived version DOI:** https://doi.org/10.5281/zenodo.22921191 (archived snapshot; not a claim that 2026 financial additions are included)

| Resource | Path | Format | Size | Git blob SHA |
|---|---|---|---:|---|
| communal-master-integrated | [`data/communal_master/chile_digital_inclusion_communes_2026_integrated.csv`](data/communal_master/chile_digital_inclusion_communes_2026_integrated.csv) | csv | 315,159 (307.8 KB) | `799d045f5f17138f4c39404a0630a91f84194fa5` |
| communal-master-dictionary | [`data/metadata/communal_master_dictionary.csv`](data/metadata/communal_master_dictionary.csv) | csv | 49,500 (48.3 KB) | `fdc944f54d93d2afc1fe8d283c2239f9000955a6` |
| layer-catalog | [`data/metadata/layer_catalog.csv`](data/metadata/layer_catalog.csv) | csv | 8,258 (8.1 KB) | `2b8ed5edd738a47edd7b4bcfc28a2df6796a9486` |
| subtel-internet-use-by-age-2025 | [`data/subtel_longitudinal/subtel_internet_use_by_age_2025.csv`](data/subtel_longitudinal/subtel_internet_use_by_age_2025.csv) | csv | 825 (0.8 KB) | `9120b757db810d3a25973eb50e620fb8d4440b34` |
| source-registry | [`data/source_registry.csv`](data/source_registry.csv) | csv | 4,460 (4.4 KB) | `d756b0c86c9fc2d47f3ca069da66f16f832cc14a` |
| ookla-national-2026q3 | [`data/ookla/chile_2026q3_summary.csv`](data/ookla/chile_2026q3_summary.csv) | csv | 847 (0.8 KB) | `987ddb3aa2d8059a7df3fbbdc558c15c8d6699d6` |
| ookla-communal-2026q3 | [`data/ookla/territorial/chile_2026q3_communes.csv`](data/ookla/territorial/chile_2026q3_communes.csv) | csv | 108,961 (106.4 KB) | `c50506d32ec31903f17b08e80a794a5fda779c81` |
| commune-geometries | [`geo/chile_communes.geojson`](geo/chile_communes.geojson) | geojson | 8,692,983 (8.29 MB) | `423a083fcebede497053237cf82b9bed9e77599f` |
| telecom-financials-2024-2026 | [`data/economics/telecom_financials_2024_2026.csv`](data/economics/telecom_financials_2024_2026.csv) | csv | 6,944 (6.8 KB) | `4115830c8c9830efd4e15a71e3a11e72ab59c53f` |

## Integrity

The repository QA compares the `bytes` and `git_blob_sha` of each declared resource against the current Git tree. Changes to a declared resource must update `datapackage.json` accordingly. Source and geographic scope for telecom financials are documented in [`data/economics/README.md`](data/economics/README.md).

Generated release metadata such as `data/metadata/release_manifest.csv` is not declared as a stable Data Package resource because it is rebuilt when repository documentation and scripts change.

The historical Zenodo DOI is an archived snapshot, not a DOI for this in-progress `main` branch.
