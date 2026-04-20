# ccf-grafana

Curated `Grafana` wrapper chart for the Cloudera Cloud Factory components catalog.

## Purpose

This chart packages upstream Helm dependencies with curated default values and a Rancher-style `questions.yaml` so it can be imported and installed more easily in CCF.

## Upstream Dependencies

- `grafana` from `https://grafana.github.io/helm-charts` at `10.5.15`

## Defaults

- Namespace: `grafana`
- Smoke profile: `default`
- Image source choice: `upstream-official`
- Chart version: `0.1.2`
- App version: `12.3.1`

## Notes

Initial defaults remain close to upstream and keep ingress off by default.

## Files

- `Chart.yaml`: chart metadata and any pinned upstream dependencies
- `values.yaml`: curated default values for CCF environments
- `questions.yaml`: catalog prompts exposed to operators
- `templates/NOTES.txt`: post-install guidance shown by Helm after install or upgrade

## References

- Source repository: `https://grafana.github.io/helm-charts`
- Project home: https://grafana.com
- Release notes: https://grafana.com/docs/grafana/latest/release-notes/
- Icon: https://artifacthub.io/image/b4fed1a7-6c8f-4945-b99d-096efa3e4116
