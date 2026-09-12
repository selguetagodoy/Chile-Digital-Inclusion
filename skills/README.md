# Repository skills

This directory contains reusable operating protocols for research and data-maintenance tasks.

## Evidence-first data ingestion

`skills/data-ingestion/SKILL.md` defines the repository standard for discovering, acquiring, transforming, validating and publishing data.

Use it for:

- adding a new public source;
- refreshing an existing source;
- extending a longitudinal series;
- creating or modifying a data-producing GitHub Actions workflow;
- integrating a new layer into the communal master;
- reviewing schema drift or source revisions.

The skill is intentionally conservative. Missing observations remain missing unless the source explicitly reports zero; incompatible statistical universes are not silently merged; and new or changed pipelines must preserve provenance and pass relevant QA gates before publication.

`skills/data-ingestion/source-config.example.yml` is a template for documenting new source integrations. Existing stable repository paths and schemas should not be reorganized solely to match the template.
