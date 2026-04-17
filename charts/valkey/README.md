# ccf-valkey

Curated `Valkey` wrapper chart for the Cloudera Cloud Factory components catalog.

## Purpose

This chart packages upstream Helm dependencies with curated default values and a Rancher-style
`questions.yaml` so it can be imported and installed more easily in CCF.

## Upstream Dependencies

- `valkey` from `https://valkey.io/valkey-helm/` at `0.9.4`

## Defaults

- Namespace: `valkey`
- Smoke profile: `default`
- Image source choice: `upstream-official`
- Chart version: `0.1.1`
- Upstream app version: `9.0.2`

## Notes

Official Valkey chart with conservative single-primary defaults.

## Files

- `Chart.yaml`: wrapper metadata and pinned upstream dependencies
- `values.yaml`: curated default values for CCF environments
- `questions.yaml`: catalog prompts exposed to operators

## References

- Upstream repository: `https://valkey.io/valkey-helm/`
- Project home: https://valkey.io/valkey-helm/
- Icon: https://dyltqmyl993wv.cloudfront.net/assets/stacks/valkey/img/valkey-stack-220x234.png
