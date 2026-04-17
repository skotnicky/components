# ccf-openmetadata

Curated `OpenMetadata` wrapper chart for the Cloudera Cloud Factory components catalog.

## Purpose

This chart packages upstream Helm dependencies with curated default values and a Rancher-style
`questions.yaml` so it can be imported and installed more easily in CCF.

## Upstream Dependencies

- `openmetadata` from `https://helm.open-metadata.org/` at `1.12.5`

## Defaults

- Namespace: `openmetadata`
- Smoke profile: `manual-only`
- Image source choice: `upstream-official`
- Chart version: `0.1.2`
- Upstream app version: `1.12.5`

## Notes

The application chart expects external database and search services for a clean non-Bitnami setup. Validation remains manual-only until those overrides are supplied.

## Files

- `Chart.yaml`: wrapper metadata and pinned upstream dependencies
- `values.yaml`: curated default values for CCF environments
- `questions.yaml`: catalog prompts exposed to operators

## References

- Upstream repository: `https://helm.open-metadata.org/`
- Project home: https://open-metadata.org/
- Icon: https://open-metadata.org/assets/favicon.png
