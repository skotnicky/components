# ccf-netbox

Curated `NetBox` wrapper chart for the Cloudera Cloud Factory components catalog.

## Purpose

This chart packages upstream Helm dependencies with curated default values and a Rancher-style
`questions.yaml` so it can be imported and installed more easily in CCF.

## Upstream Dependencies

- `netbox` from `https://charts.netbox.oss.netboxlabs.com/` at `8.1.1`

## Defaults

- Namespace: `netbox`
- Smoke profile: `manual-only`
- Image source choice: `upstream-official`
- Chart version: `0.1.1`
- Upstream app version: `v4.5.8`

## Notes

The community chart currently depends on Bitnami common/postgresql/valkey artifacts. Validation remains manual-only while external service wiring is supplied.

## Files

- `Chart.yaml`: wrapper metadata and pinned upstream dependencies
- `values.yaml`: curated default values for CCF environments
- `questions.yaml`: catalog prompts exposed to operators

## References

- Upstream repository: `https://charts.netbox.oss.netboxlabs.com/`
- Project home: https://netbox.dev/
- Icon: https://raw.githubusercontent.com/netbox-community/netbox/main/docs/netbox_logo_light.svg
