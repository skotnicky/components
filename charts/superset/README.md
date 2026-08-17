# ccf-superset

Curated `Apache Superset` wrapper chart for the Cloudera Cloud Factory components catalog.

## Purpose

This chart packages upstream Helm dependencies with curated default values and a Rancher-style `questions.yaml` so it can be imported and installed more easily in CCF.

## Upstream Dependencies

- `superset` from `https://apache.github.io/superset` at `0.22.4`

## Defaults

- Namespace: `superset`
- Smoke profile: `manual-only`
- Image source choice: `upstream-official`
- Chart version: `0.1.0`
- App version: `6.1.0`

## Notes

Official Apache Superset chart with Bitnami PostgreSQL and Redis dependencies disabled. Defaults expect external PostgreSQL and Valkey services, such as CloudNativePG and the curated Valkey chart, and remain manual-only until project-specific credentials and service DNS are supplied.

## Files

- `Chart.yaml`: chart metadata and any pinned upstream dependencies
- `values.yaml`: curated default values for CCF environments
- `questions.yaml`: catalog prompts exposed to operators
- `templates/NOTES.txt`: post-install guidance shown by Helm after install or upgrade

## References

- Source repository: `https://apache.github.io/superset`
- Project home: https://superset.apache.org/
- Release notes: https://github.com/apache/superset/releases
- Icon: https://superset.apache.org/img/superset-logo-horiz.svg
