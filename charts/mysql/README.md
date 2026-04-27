# ccf-mysql

Curated `MySQL` wrapper chart for the Cloudera Cloud Factory components catalog.

## Purpose

This chart packages upstream Helm dependencies with curated default values and a Rancher-style `questions.yaml` so it can be imported and installed more easily in CCF.

## Upstream Dependencies

- `mysql` from `https://repo.helmforge.dev` at `1.8.6`

## Defaults

- Namespace: `mysql`
- Smoke profile: `manual-only`
- Image source choice: `upstream-official`
- Chart version: `0.1.1`
- App version: `8.4`

## Notes

Standalone MySQL service chart used as a non-Bitnami backend option for applications such as OpenMetadata. Defaults stay single-instance and internal-only for CCF projects. When `mysql.auth.existingSecret` is used, the upstream chart expects `mysql-root-password`, `mysql-user-password`, and `mysql-replication-password` keys.

## Files

- `Chart.yaml`: chart metadata and any pinned upstream dependencies
- `values.yaml`: curated default values for CCF environments
- `questions.yaml`: catalog prompts exposed to operators
- `templates/NOTES.txt`: post-install guidance shown by Helm after install or upgrade

## References

- Source repository: `https://repo.helmforge.dev`
- Project home: https://www.mysql.com/
- Release notes: https://dev.mysql.com/doc/relnotes/mysql/8.4/en/
