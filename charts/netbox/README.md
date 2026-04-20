# ccf-netbox

Curated `NetBox` standalone chart for the Cloudera Cloud Factory components catalog.

## Purpose

This chart is maintained directly in this repository so NetBox can be installed without depending on upstream Bitnami-backed PostgreSQL and Valkey chart packaging.

## Upstream Dependencies

This chart has no external Helm dependencies.

## Defaults

- Namespace: `netbox`
- Smoke profile: `manual-only`
- Image source choice: `upstream-official`
- Chart version: `0.1.2`
- App version: `v4.5.8`

## Notes

Standalone curated chart that removes the upstream Bitnami-backed PostgreSQL and Valkey dependency path. It expects external PostgreSQL and Valkey services, keeping validation manual-only until project-specific credentials and service DNS are supplied.

## Files

- `Chart.yaml`: chart metadata and any pinned upstream dependencies
- `values.yaml`: curated default values for CCF environments
- `questions.yaml`: catalog prompts exposed to operators
- `templates/NOTES.txt`: post-install guidance shown by Helm after install or upgrade

## References

- Source repository: `local://components/netbox`
- Project home: https://netbox.dev/
- Release notes: https://github.com/netbox-community/netbox/releases
- Icon: https://raw.githubusercontent.com/netbox-community/netbox/main/docs/netbox_logo_light.svg
