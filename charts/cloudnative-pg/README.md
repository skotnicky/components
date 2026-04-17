# ccf-cloudnative-pg

Curated `CloudNativePG` wrapper chart for the Cloudera Cloud Factory components catalog.

## Purpose

This chart packages upstream Helm dependencies with curated default values and a Rancher-style
`questions.yaml` so it can be imported and installed more easily in CCF.

## Upstream Dependencies

- `cloudnative-pg` from `https://cloudnative-pg.github.io/charts` at `0.28.0`

## Defaults

- Namespace: `cnpg-system`
- Smoke profile: `default`
- Image source choice: `upstream-official`
- Chart version: `0.1.1`
- Upstream app version: `1.29.0`

## Notes

Namespace-scoped operator defaults are used for safer CCF project installs.

## Files

- `Chart.yaml`: wrapper metadata and pinned upstream dependencies
- `values.yaml`: curated default values for CCF environments
- `questions.yaml`: catalog prompts exposed to operators

## References

- Upstream repository: `https://cloudnative-pg.github.io/charts`
- Project home: https://cloudnative-pg.io
- Icon: https://raw.githubusercontent.com/cloudnative-pg/artwork/main/cloudnativepg-logo.svg
