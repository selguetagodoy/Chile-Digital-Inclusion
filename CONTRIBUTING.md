# Contributing

Corrections and evidence-backed improvements are welcome. These repositories are research products, so changes must preserve **traceability, comparability and source boundaries**.

## Preferred route for data corrections

Use the repository issue form **Data correction / evidence update**. It requires the minimum information needed to reproduce and evaluate a proposed change.

A substantive correction should identify:

1. **Affected object** — dataset, file, field, row, chart, source, transformation or documentation section.
2. **Current published value or statement**.
3. **Exact proposed correction**.
4. **Primary source** — preferably an official or technically authoritative URL, document or persistent identifier.
5. **Reference period** — publication date and statistical period where relevant.
6. **Geographic and statistical universe**.
7. **Unit and precision**.
8. **Evidence type** — observed, derived, estimated or proxy.
9. **Comparability impact** — any effect on definitions, source family, historical series, territorial boundaries or derived indicators.

Screenshots, secondary summaries or search snippets are not sufficient when the underlying source is available.

## Integrity rules

- Do not fill missing values by assumption.
- Do not interpolate or extrapolate unless the project methodology explicitly defines and labels that transformation.
- Do not silently replace one statistical universe with another.
- Do not overwrite a historical vintage with a newer observation.
- Preserve methodological breaks between source families.
- Distinguish observed values, proxies and derived indicators.
- Preserve ranges when the source reports a range; do not invent a midpoint.
- Keep operational, planned, announced and derived infrastructure categories separate.
- For regulatory or institutional information, prefer the official legal or institutional source.
- Preserve source-specific licensing and attribution requirements.

## Corrections versus new versions

A transcription, metadata or documentation correction may be applied to the working branch and recorded in `CHANGELOG.md`.

A change that materially alters published results, methodology, coverage or a citable snapshot should normally be associated with a new versioned release rather than silently rewriting a published version.

## Pull requests

When submitting a pull request:

- keep unrelated changes separate;
- explain the evidence and transformation logic;
- update provenance or source ledgers where applicable;
- update documentation when a definition changes;
- preserve stable identifiers unless there is a documented reason to change them;
- run the repository validation workflows before merging.

## Citation and rights

Contributing evidence does not transfer ownership of third-party source material. Original source terms and attribution requirements remain applicable.

See:

- `SOURCE_OF_TRUTH.md` for the evidence hierarchy;
- `NOTICE.md` for authorship and reuse boundaries;
- `CITATION.cff`, `CITATION.bib` and `codemeta.json` for citation metadata.

The project author retains editorial responsibility for public releases and may request additional evidence before incorporating a change.
