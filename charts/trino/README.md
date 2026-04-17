# ccf-trino

Curated `Trino` wrapper chart for the Cloudera Cloud Factory components catalog.

## Purpose

This chart packages upstream Helm dependencies with curated default values and a Rancher-style
`questions.yaml` so it can be imported and installed more easily in CCF.

## Upstream Dependencies

- `trino` from `https://trinodb.github.io/charts/` at `1.42.1`

## Defaults

- Namespace: `trino`
- Smoke profile: `default`
- Image source choice: `upstream-official`
- Chart version: `0.1.1`
- Upstream app version: `479`

## Notes

Internal-only service defaults keep Trino easy to validate inside a project.

## Files

- `Chart.yaml`: wrapper metadata and pinned upstream dependencies
- `values.yaml`: curated default values for CCF environments
- `questions.yaml`: catalog prompts exposed to operators

## References

- Upstream repository: `https://trinodb.github.io/charts/`
- Project home: https://trino.io/
- Icon: https://trino.io/assets/trino.png
