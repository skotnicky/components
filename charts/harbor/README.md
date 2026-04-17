# ccf-harbor

Curated `Harbor` wrapper chart for the Cloudera Cloud Factory components catalog.

## Purpose

This chart packages upstream Helm dependencies with curated default values and a Rancher-style
`questions.yaml` so it can be imported and installed more easily in CCF.

## Upstream Dependencies

- `harbor` from `https://helm.goharbor.io` at `1.18.3`

## Defaults

- Namespace: `harbor`
- Smoke profile: `needs-overrides`
- Image source choice: `upstream-official`
- Chart version: `0.1.2`
- Upstream app version: `2.14.3`

## Notes

Official Harbor chart. Initial defaults keep upstream images because Harbor ships multiple tightly coupled components.

## Files

- `Chart.yaml`: wrapper metadata and pinned upstream dependencies
- `values.yaml`: curated default values for CCF environments
- `questions.yaml`: catalog prompts exposed to operators

## References

- Upstream repository: `https://helm.goharbor.io`
- Project home: https://goharbor.io
- Icon: https://raw.githubusercontent.com/goharbor/website/main/static/img/logos/harbor-icon-color.png
