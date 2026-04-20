# ccf-chaos-mesh

Curated `Chaos Mesh` wrapper chart for the Cloudera Cloud Factory components catalog.

## Purpose

This chart packages upstream Helm dependencies with curated default values and a Rancher-style `questions.yaml` so it can be imported and installed more easily in CCF.

## Upstream Dependencies

- `chaos-mesh` from `https://charts.chaos-mesh.org` at `2.8.2`

## Defaults

- Namespace: `chaos-mesh`
- Smoke profile: `needs-overrides`
- Image source choice: `upstream-official`
- Chart version: `0.1.2`
- App version: `2.8.2`

## Notes

Dashboard is normalized to ClusterIP instead of the upstream NodePort default.

## Files

- `Chart.yaml`: chart metadata and any pinned upstream dependencies
- `values.yaml`: curated default values for CCF environments
- `questions.yaml`: catalog prompts exposed to operators
- `templates/NOTES.txt`: post-install guidance shown by Helm after install or upgrade

## References

- Source repository: `https://charts.chaos-mesh.org`
- Project home: https://chaos-mesh.org
- Release notes: https://github.com/chaos-mesh/chaos-mesh/releases
- Icon: https://raw.githubusercontent.com/chaos-mesh/chaos-mesh/master/static/logo.svg
