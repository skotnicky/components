# ccf-minio-operator

Curated `MinIO Operator` wrapper chart for the Cloudera Cloud Factory components catalog.

## Purpose

This chart packages upstream Helm dependencies with curated default values and a Rancher-style `questions.yaml` so it can be imported and installed more easily in CCF.

## Upstream Dependencies

- `operator` from `https://operator.min.io/` at `7.1.1`

## Defaults

- Namespace: `minio-operator`
- Smoke profile: `default`
- Image source choice: `upstream-official`
- Chart version: `0.1.0`
- App version: `v7.1.1`

## Notes

Official MinIO operator chart for S3-compatible object storage. Defaults keep a single operator replica for easier CCF project validation.

## Files

- `Chart.yaml`: chart metadata and any pinned upstream dependencies
- `values.yaml`: curated default values for CCF environments
- `questions.yaml`: catalog prompts exposed to operators
- `templates/NOTES.txt`: post-install guidance shown by Helm after install or upgrade

## References

- Source repository: `https://operator.min.io/`
- Project home: https://min.io
- Release notes: https://github.com/minio/operator/releases
- Icon: https://min.io/resources/img/logo/MINIO_wordmark.png
