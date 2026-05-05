# ccf-airflow

Curated `Apache Airflow` wrapper chart for the Cloudera Cloud Factory components catalog.

## Purpose

This chart packages upstream Helm dependencies with curated default values and a Rancher-style `questions.yaml` so it can be imported and installed more easily in CCF.

## Upstream Dependencies

- `airflow` from `https://airflow.apache.org` at `1.21.0`

## Defaults

- Namespace: `airflow`
- Smoke profile: `manual-only`
- Image source choice: `upstream-official`
- Chart version: `0.1.0`
- App version: `3.2.0`

## Notes

Official Apache Airflow chart with conservative defaults for CCF projects.

## Files

- `Chart.yaml`: chart metadata and any pinned upstream dependencies
- `values.yaml`: curated default values for CCF environments
- `questions.yaml`: catalog prompts exposed to operators
- `templates/NOTES.txt`: post-install guidance shown by Helm after install or upgrade

## References

- Source repository: `https://airflow.apache.org`
- Project home: https://airflow.apache.org/
- Release notes: https://airflow.apache.org/docs/apache-airflow/stable/release_notes.html
- Icon: https://airflow.apache.org/images/feature-image.png
