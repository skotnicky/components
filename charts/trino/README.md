# ccf-trino

Curated `Trino` wrapper chart for the Cloudera Cloud Factory components catalog.

## Purpose

This chart packages upstream Helm dependencies with curated default values and a Rancher-style `questions.yaml` so it can be imported and installed more easily in CCF.

## Upstream Dependencies

- `trino` from `https://trinodb.github.io/charts/` at `1.42.1`

## Defaults

- Namespace: `trino`
- Smoke profile: `default`
- Image source choice: `upstream-official`
- Chart version: `0.1.2`
- App version: `479`

## Notes

Internal-only service defaults keep Trino easy to validate inside a project.

## Files

- `Chart.yaml`: chart metadata and any pinned upstream dependencies
- `values.yaml`: curated default values for CCF environments
- `questions.yaml`: catalog prompts exposed to operators
- `templates/NOTES.txt`: post-install guidance shown by Helm after install or upgrade

## References

- Source repository: `https://trinodb.github.io/charts/`
- Project home: https://trino.io/
- Release notes: https://trino.io/docs/current/release.html
- Icon: https://trino.io/assets/trino.png
