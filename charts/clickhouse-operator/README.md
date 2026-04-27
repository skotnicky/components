# ccf-clickhouse-operator

Curated `ClickHouse Operator` wrapper chart for the Cloudera Cloud Factory components catalog.

## Purpose

This chart packages upstream Helm dependencies with curated default values and a Rancher-style `questions.yaml` so it can be imported and installed more easily in CCF.

## Upstream Dependencies

- `clickhouse-operator-helm` from `oci://ghcr.io/clickhouse` at `0.0.4`

## Defaults

- Namespace: `clickhouse-operator`
- Smoke profile: `default`
- Image source choice: `upstream-official`
- Chart version: `0.1.3`
- App version: `v0.0.4`

## Notes

Official ClickHouse operator chart from GHCR OCI.

## Files

- `Chart.yaml`: chart metadata and any pinned upstream dependencies
- `values.yaml`: curated default values for CCF environments
- `questions.yaml`: catalog prompts exposed to operators
- `templates/NOTES.txt`: post-install guidance shown by Helm after install or upgrade

## References

- Source repository: `oci://ghcr.io/clickhouse`
- Project home: https://github.com/ClickHouse/clickhouse-operator
- Release notes: https://github.com/ClickHouse/clickhouse-operator/releases
- Icon: https://clickhouse.com/docs/img/clickhouse-operator-logo.svg
