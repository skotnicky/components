# Versioning Policy

## Curated Wrapper Charts

Curated wrapper charts use independent chart versions and pinned upstream dependency versions.

Rules:

- bump the curated chart version whenever dependency versions or default values change
- preserve upstream dependency pins through `scripts/catalog_state.json`
- regenerate the wrapper charts after metadata changes with `python3 scripts/render_catalog.py`
- never reuse an already published curated chart version

Suggested interpretation:

- patch bump: documentation-only or non-functional metadata changes
- minor bump: default value changes, `questions.yaml` changes, or validation profile changes
- major bump: breaking default changes or incompatible upstream dependency moves

## Update Automation

The `update-upstreams.yml` workflow checks for newer upstream curated chart versions, writes the
next pinned dependency versions to `scripts/catalog_state.json`, bumps the wrapper chart patch
version, opens a pull request, and enables auto-merge.

Repository auto-merge must be enabled in GitHub settings for that workflow to finish the merge
automatically.

The `release-oci.yml` workflow publishes curated wrapper charts after validation.

The `publish-helm-repo.yml` workflow preserves already released chart archives and merges the new
`index.yaml` entries so the GitHub Pages Helm repository remains append-only.
