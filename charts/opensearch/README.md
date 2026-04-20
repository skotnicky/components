# ccf-opensearch

Curated `OpenSearch` wrapper chart for the Cloudera Cloud Factory components catalog.

## Purpose

This chart packages upstream Helm dependencies with curated default values and a Rancher-style `questions.yaml` so it can be imported and installed more easily in CCF.

## Upstream Dependencies

- `opensearch` from `https://opensearch-project.github.io/helm-charts/` at `3.1.0`

## Defaults

- Namespace: `opensearch`
- Smoke profile: `manual-only`
- Image source choice: `upstream-official`
- Chart version: `0.1.0`
- App version: `3.1.0`

## Notes

Official OpenSearch chart packaged as a non-Bitnami backend option for applications such as OpenMetadata. Defaults stay internal-only and single-node for CCF projects.

## Files

- `Chart.yaml`: chart metadata and any pinned upstream dependencies
- `values.yaml`: curated default values for CCF environments
- `questions.yaml`: catalog prompts exposed to operators
- `templates/NOTES.txt`: post-install guidance shown by Helm after install or upgrade

## References

- Source repository: `https://opensearch-project.github.io/helm-charts/`
- Project home: https://opensearch.org/
- Release notes: https://github.com/opensearch-project/OpenSearch/releases
