# ccf-openmetadata

Curated `OpenMetadata` wrapper chart for the Cloudera Cloud Factory components catalog.

## Purpose

This chart packages upstream Helm dependencies with curated default values and a Rancher-style `questions.yaml` so it can be imported and installed more easily in CCF.

## Upstream Dependencies

- `openmetadata` from `https://helm.open-metadata.org/` at `1.12.5`

## Defaults

- Namespace: `openmetadata`
- Smoke profile: `manual-only`
- Image source choice: `upstream-official`
- Chart version: `0.1.2`
- App version: `1.12.5`

## Notes

The application chart expects external MySQL and OpenSearch services for a clean non-Bitnami setup. Curated companion backend charts are available in this catalog, but application wiring remains manual-only until project-specific hostnames and credentials are supplied. The default pipeline client type is Kubernetes so disabled installs do not require an Airflow secret; switch back to Airflow only when the `airflow-secrets` Secret is present.

## Files

- `Chart.yaml`: chart metadata and any pinned upstream dependencies
- `values.yaml`: curated default values for CCF environments
- `questions.yaml`: catalog prompts exposed to operators
- `templates/NOTES.txt`: post-install guidance shown by Helm after install or upgrade

## References

- Source repository: `https://helm.open-metadata.org/`
- Project home: https://open-metadata.org/
- Release notes: https://github.com/open-metadata/OpenMetadata/releases
- Icon: https://open-metadata.org/assets/favicon.png
