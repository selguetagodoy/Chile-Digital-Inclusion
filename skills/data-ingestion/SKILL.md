---
name: evidence-first-data-ingestion
description: Reusable protocol for adding, refreshing, validating and publishing public datasets in Chile Digital Inclusion and related research repositories without inventing, interpolating or silently harmonizing evidence.
version: 1.0.0
---

# Evidence-first data ingestion

## Purpose

Use this skill whenever a task adds a new public data source, refreshes an existing source, rebuilds a derived dataset, extends a longitudinal series, or creates a GitHub Actions workflow that changes published data.

The objective is not to maximize completeness. The objective is to maximize traceability, reproducibility and comparability while preserving source limitations.

## Core contract

Every published value must be recoverable to an identifiable source, transformation and validation path.

The ingestion pipeline follows this order:

```text
source discovery
    -> acquisition
    -> raw/source preservation or reproducible retrieval
    -> structural profiling
    -> semantic mapping
    -> transformation
    -> QA and reconciliation
    -> derived/public output
    -> metadata and provenance
    -> validation
    -> commit / pull request / release
```

A pipeline is incomplete if it publishes a value before provenance and QA are resolved.

## Non-negotiable rules

1. Never invent a missing observation.
2. Never interpolate or extrapolate a missing value unless the repository explicitly defines a separate modeled product and labels it as modeled.
3. Never replace a missing value with zero unless the source explicitly defines the observation as zero.
4. Never convert ranges to midpoints for publication as observed data.
5. Never merge different statistical universes as if they had the same denominator.
6. Never treat administrative counts, survey estimates, network tests, infrastructure records or program beneficiaries as interchangeable measures.
7. Never use a secondary source when the primary source is available and machine-readable, unless the secondary source is explicitly required for validation.
8. Never bypass authentication, paywalls, tokens or access controls.
9. Never silently revise historical observations. A source revision must remain detectable through version control or provenance metadata.
10. Never publish person-level microdata, direct identifiers, proprietary weights or restricted source material.
11. Preserve the source's published precision. Do not fabricate additional decimals.
12. Record unresolved ambiguity as unresolved. Do not force a mapping only to eliminate N/D.

## Source priority

Prefer sources in this order:

1. official API or official structured endpoint;
2. official CSV, Parquet, JSON, GeoJSON or XLSX;
3. official database export;
4. official HTML table;
5. official PDF with extractable structured evidence;
6. authoritative secondary source when the primary source is unavailable;
7. manual evidence only when no reproducible structured source exists.

When two official publications disagree, preserve both observations with separate provenance and document the discrepancy. Do not average them.

## Statistical-unit gate

Before transforming data, identify:

- publisher;
- dataset;
- observation period;
- publication date, when available;
- statistical unit;
- geographic unit;
- denominator or expansion weight;
- unit of measure;
- update frequency;
- source URL or endpoint;
- source version or file identifier, when available;
- licensing or attribution constraints.

Stop the integration if the statistical unit or denominator cannot be determined and the ambiguity would affect interpretation.

## Acquisition modes

### API / structured endpoint

Store the endpoint and query parameters in code or metadata. Paginate explicitly. Check HTTP status and schema before processing.

### CSV / XLSX / Parquet / JSON / GeoJSON

Download from the publisher. Preserve a checksum when practical. Profile sheets, headers, row counts and types before selecting fields.

### ArcGIS / geospatial services

Enumerate available services and layers first. Record service name, geometry type, field schema, record count and accessibility state. Exclude token-protected layers rather than attempting to circumvent access control.

### PDF

Use only when the required evidence is not available in a structured official source. Extract explicit published values and retain page/table provenance. Do not infer unlabeled values from chart geometry unless the project explicitly defines and documents a chart-digitization method.

### Temporary restricted-size source files

If licensing or repository-size constraints make source retention inappropriate, retrieve the official source during workflow execution, publish only permitted aggregates/metadata, and document the retrieval path.

## Raw and derived layers

When source retention is permitted, prefer:

```text
data/raw/<source_id>/
data/processed/<source_id>/
data/metadata/
```

Existing repository-specific layouts may be preserved. Do not reorganize stable public paths solely to satisfy this convention.

Raw/source artifacts are immutable evidence. Processed/public artifacts may be regenerated from code.

If the raw source is intentionally not stored, the workflow must contain enough information to retrieve the same public source again or explain why exact retrieval is no longer possible.

## Required source manifest for new pipelines

For each new source or materially changed source, maintain equivalent metadata to:

```yaml
source_id: unique_machine_name
publisher: official publisher
dataset: official dataset title
source_url: canonical URL or endpoint
source_type: api|csv|xlsx|parquet|json|geojson|arcgis|pdf|other
publication_date: YYYY-MM-DD|null
observation_start: YYYY-MM-DD|null
observation_end: YYYY-MM-DD|null
retrieved_at: ISO-8601 timestamp
statistical_unit: household|person|connection|test|record|establishment|territory|other
geographic_unit: national|region|province|commune|point|line|polygon|other
unit: explicit source unit
denominator_or_weight: explicit denominator, weight or not_applicable
license: source license or terms
checksum: sha256 when applicable
status: verified|pending_review|source_changed|not_available
notes: concise methodological caveat
```

Existing `data/source_registry.csv` remains a compact public registry. Do not change its schema casually because downstream code may depend on it.

## Structural profiling

Before building the final dataset, inspect and record as appropriate:

- workbook sheets;
- column names;
- row counts;
- data types;
- null counts;
- duplicate keys;
- unexpected categories;
- geographic codes;
- formulas and subtotal rows in spreadsheets;
- source-level totals;
- schema changes versus the previous release.

A source schema change is a first-class event. If headers, sheet names, categories or units change, mark the source as `source_changed` until the mapping is reviewed.

## Transformation rules

Transformations must be explicit and deterministic.

Allowed examples:

- rename fields while preserving a documented mapping;
- convert source dates into ISO dates;
- reshape wide data to long format;
- aggregate when the aggregation is mathematically valid for the statistical unit;
- spatially assign records using a documented method;
- calculate ratios when numerator and denominator are independently valid and compatible;
- calculate period-to-period changes from observed values.

High-risk transformations requiring explicit methodological documentation:

- crosswalks between changing geographic codes;
- category harmonization across survey waves;
- reconstruction from spreadsheet subtotal blocks;
- deduplication where the source lacks a stable identifier;
- spatial assignment near boundaries;
- weighted survey estimation;
- combining data from distinct publishers.

Prohibited by default:

- midpoint of a published range presented as observed value;
- backcasting;
- forward filling;
- linear interpolation;
- proxy substitution without a separately named indicator;
- synthetic latency, efficiency, cost or performance observations;
- arbitrary pipeline probabilities or scores;
- hiding source disagreement through averaging.

## Comparability gate

Before appending a new period to a longitudinal series, verify:

1. same concept;
2. same or explicitly mapped unit;
3. same statistical universe;
4. same denominator/weight logic;
5. same geographic scope;
6. compatible measurement method;
7. no unhandled category break.

If one of these fails, either create a new series/field or insert an explicit comparability break. Do not force continuity.

## QA gates

Every ingestion should implement the checks that are material for that source.

Minimum checks:

- expected key uniqueness;
- expected row-count range;
- required columns present;
- numeric fields parse correctly;
- impossible values rejected;
- missingness reported;
- duplicate observations reported;
- source period verified;
- source totals reconciled when totals exist;
- output-to-source linkage preserved.

Additional checks when relevant:

- regional subtotal reconciliation;
- national total reconciliation;
- spatial assignment coverage;
- crosswalk match rate;
- weighted vs published control estimate;
- schema drift detection;
- checksum comparison;
- previous-release delta review;
- dashboard/public-contract validation.

A QA failure must stop publication when it affects correctness, key integrity or provenance.

## Missing values

Use missingness as information.

Distinguish, when supported by evidence:

- `not_reported` — source does not report the value;
- `source_blank` — source contains an explicit blank position;
- `not_applicable` — concept does not apply;
- `not_available` — source could not be obtained;
- `pending_review` — evidence exists but mapping is unresolved.

Do not collapse these states into zero.

## Provenance fields for row-level or long-format data

When practical, include:

```text
source_id
source_period
source_url
source_file
source_sheet_or_table
source_row_or_record
retrieved_at
transformation
qa_status
```

For compact public datasets, equivalent provenance may live in a companion manifest rather than every row.

## GitHub Actions conventions

New automated source workflows should normally:

1. support `workflow_dispatch`;
2. pin the Python major/minor version used by the repository;
3. install only required dependencies;
4. execute acquisition/transformation through a versioned script;
5. print compact QA summaries;
6. stage only files owned by that pipeline;
7. commit only when the generated outputs changed;
8. use the repository concurrency group for writers when multiple workflows can update `main`;
9. run or trigger the relevant validation contract;
10. avoid embedding credentials in code or logs.

For this repository, preserve the existing `main-writers` concurrency pattern for workflows that commit generated outputs.

A generic writer block is:

```bash
git config user.name 'github-actions[bot]'
git config user.email '41898282+github-actions[bot]@users.noreply.github.com'
git add <pipeline-owned-paths>
if git diff --cached --quiet; then
  echo 'No changes to commit'
else
  git commit -m '<descriptive data update>'
  git pull --rebase origin main
  git push
fi
```

Do not use `git add .` in data-generation workflows.

## Repository-specific integration contract

For `Chile-Digital-Inclusion`:

- the canonical integrated communal product is `data/communal_master/chile_digital_inclusion_communes_2026_integrated.csv`;
- the canonical variable dictionary is `data/metadata/communal_master_dictionary.csv`;
- `data/source_registry.csv` is the compact source registry;
- `data/metadata/layer_catalog.csv` catalogs canonical and audit layers;
- `data/metadata/release_manifest.csv` inventories public files and checksums;
- `data/metadata/public_release_validation.csv` records the public-release validation state;
- `docs/reproducibility.md` is the primary architecture and reconstruction reference;
- `validate-public-release.yml` is the public release contract gate.

New integrations must not change the meaning of an existing public field silently. If semantics change, create a new field or document a versioned break.

## Workflow for adding a new source

### Phase 1 — discover

1. Locate the primary official source.
2. Record canonical URL and publisher.
3. Determine update frequency and latest observation period.
4. Check licensing/access conditions.
5. Identify structured alternatives before using PDF/manual extraction.

### Phase 2 — profile

1. Download or query the source.
2. Inventory schema and dimensions.
3. Identify statistical unit and denominator.
4. Detect duplicates, totals, formulas, blanks and category changes.
5. Compare with the prior release when one exists.

### Phase 3 — build

1. Create or update a script under `scripts/`.
2. Keep source-specific parsing separate from integration logic when practical.
3. Generate audit artifacts before final public artifacts.
4. Preserve missingness semantics.
5. Add provenance metadata.

### Phase 4 — validate

1. Run source-level QA.
2. Reconcile official totals where available.
3. Check key uniqueness and row count.
4. Validate comparability with historical observations.
5. Run repository-level validation if public products changed.

### Phase 5 — publish

1. Update the source registry or companion metadata.
2. Update methodology/reproducibility documentation when interpretation changes.
3. Commit generated artifacts only after QA passes.
4. Prefer a pull request for new pipelines, schema changes or methodological changes.
5. Use direct automated commits only for established, deterministic refresh pipelines.

## Workflow for refreshing an existing source

1. Retrieve the latest official publication.
2. Compare file/schema/checksum with the previous release.
3. If schema is unchanged, run the existing pipeline.
4. If schema changed, stop automatic publication and review the mapping.
5. Compare generated outputs with the previous committed version.
6. Flag large or directionally surprising deltas for review; do not suppress them merely because they are surprising.
7. Run all source and release validation gates.
8. Commit only verified changes.

## Completion report

At the end of an ingestion task, report:

```text
Source:
Latest observation period:
Source type:
Files added/updated:
Rows/records processed:
Missing values introduced/resolved:
QA checks:
Reconciliations:
Schema changes:
Comparability warnings:
Publication status: VERIFIED | PENDING_REVIEW | SOURCE_CHANGED | NOT_AVAILABLE
```

Do not describe a pipeline as complete if validation is still pending.

## Decision rule

When completeness conflicts with evidence quality, preserve the gap and document it.

A defensible `N/D` is preferable to an invented observation.
