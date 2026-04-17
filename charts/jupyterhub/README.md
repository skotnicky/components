# ccf-jupyterhub

Curated `JupyterHub` wrapper chart for the Cloudera Cloud Factory components catalog.

## Purpose

This chart packages upstream Helm dependencies with curated default values and a Rancher-style
`questions.yaml` so it can be imported and installed more easily in CCF.

## Upstream Dependencies

- `jupyterhub` from `https://hub.jupyter.org/helm-chart/` at `4.3.3`

## Defaults

- Namespace: `jupyterhub`
- Smoke profile: `needs-overrides`
- Image source choice: `upstream-official`
- Chart version: `0.1.1`
- Upstream app version: `5.4.4`

## Notes

Proxy service is normalized to ClusterIP to fit most CCF projects.

## Files

- `Chart.yaml`: wrapper metadata and pinned upstream dependencies
- `values.yaml`: curated default values for CCF environments
- `questions.yaml`: catalog prompts exposed to operators

## References

- Upstream repository: `https://hub.jupyter.org/helm-chart/`
- Project home: https://z2jh.jupyter.org
- Icon: https://hub.jupyter.org/helm-chart/images/hublogo.svg
