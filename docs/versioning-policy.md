# Versioning Policy

## Curated Wrapper Charts

Curated wrapper charts use independent chart versions and pinned upstream dependency versions.

Rules:

- bump the curated chart version whenever dependency versions or default values change
- preserve explicit upstream dependency versions in `scripts/catalog_data.py`
- regenerate the wrapper charts after metadata changes with `python3 scripts/render_catalog.py`

Suggested interpretation:

- patch bump: documentation-only or non-functional metadata changes
- minor bump: default value changes, `questions.yaml` changes, or validation profile changes
- major bump: breaking default changes or incompatible upstream dependency moves

## Update Automation

The `update-upstreams.yml` workflow checks for newer upstream curated chart versions and writes a report to `reports/upstream-updates.json`.

The `release-oci.yml` workflow publishes curated wrapper charts after validation.
