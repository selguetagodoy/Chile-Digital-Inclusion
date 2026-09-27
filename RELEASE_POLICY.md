# Release and archival policy

This repository is maintained as a versioned public research object. GitHub releases and Zenodo records have distinct roles and must not be treated as interchangeable until the archived record is verified.

## Metadata authority

- `CITATION.cff` is the primary repository citation metadata used by GitHub and is kept aligned with the latest confirmed citable release.
- `CITATION.bib` provides a human-portable BibTeX citation.
- `codemeta.json` provides machine-readable research metadata.
- `datapackage.json` describes the public data resources included in the working repository.
- `research-portfolio.json` in the author's profile repository records the canonical landing, current GitHub release and latest confirmed citable version.

This repository intentionally does **not** use `.zenodo.json` unless a future release requires Zenodo-specific metadata that cannot be expressed safely through the existing open metadata. When both files are present, Zenodo prioritizes `.zenodo.json` over `CITATION.cff`.

## Release sequence

For a material public release:

1. finalize data, documentation and source provenance;
2. run repository QA and resolve failures;
3. update `CHANGELOG.md`, `CITATION.cff`, `CITATION.bib`, `codemeta.json` and `datapackage.json`;
4. create the Git tag and GitHub release;
5. archive the release in Zenodo when the repository/integration is enabled;
6. verify the resulting Zenodo record and version DOI;
7. only then update the canonical landing page, public dataset catalog and research portfolio with the confirmed version DOI.

A DOI must never be predicted, inferred or published before the Zenodo record exists.

## Version semantics

- **Patch release:** correction that does not materially change methodology or analytical coverage.
- **Minor release:** new public data, new coverage, substantial documentation or a backward-compatible methodological extension.
- **Major release:** material redesign of methodology, data model, statistical universe or interpretation that breaks direct comparability.

Historical citable snapshots are not silently rewritten. A newer working branch or GitHub release may temporarily be newer than the latest Zenodo-archived version; when that happens, public metadata must state the distinction explicitly.

## Third-party source rights

Versioning this repository does not relicense upstream data. Source-specific attribution, reuse restrictions and licensing continue to apply as documented in `NOTICE.md`, source registries and original publisher terms.
