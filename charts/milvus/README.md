# ccf-milvus

Curated `Milvus` wrapper chart for the Cloudera Cloud Factory components catalog.

## Purpose

This chart packages upstream Helm dependencies with curated default values and a Rancher-style `questions.yaml` so it can be imported and installed more easily in CCF.

## Upstream Dependencies

- `milvus` from `https://zilliztech.github.io/milvus-helm/` at `5.0.25`

## Defaults

- Namespace: `milvus`
- Smoke profile: `needs-overrides`
- Image source choice: `upstream-official`
- Chart version: `0.1.0`
- App version: `2.6.21`

## Notes

Official Zilliztech Milvus chart with standalone defaults for CCF projects. Bundled Pulsar and Kafka are disabled, etcd and MinIO stay enabled with single-replica sizing, and live validation usually needs storage-class and resource overrides.

## Files

- `Chart.yaml`: chart metadata and any pinned upstream dependencies
- `values.yaml`: curated default values for CCF environments
- `questions.yaml`: catalog prompts exposed to operators
- `templates/NOTES.txt`: post-install guidance shown by Helm after install or upgrade

## References

- Source repository: `https://zilliztech.github.io/milvus-helm/`
- Project home: https://milvus.io/
- Release notes: https://github.com/milvus-io/milvus/releases
- Icon: https://raw.githubusercontent.com/milvus-io/docs/master/v1.0.0/assets/milvus_logo.png
