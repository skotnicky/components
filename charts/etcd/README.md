# ccf-etcd

Curated `etcd` wrapper chart for the Cloudera Cloud Factory components catalog.

## Purpose

This chart packages upstream Helm dependencies with curated default values and a Rancher-style `questions.yaml` so it can be imported and installed more easily in CCF.

## Upstream Dependencies

- `etcd` from `https://groundhog2k.github.io/helm-charts/` at `1.1.12`

## Defaults

- Namespace: `etcd`
- Smoke profile: `default`
- Image source choice: `upstream-official`
- Chart version: `0.1.0`
- App version: `v3.7.1`

## Notes

Community groundhog2k etcd chart built on the official CoreOS etcd image (non-Bitnami). Provides a key-value store suitable as the metadata backend for Milvus and other components. Defaults stay single-node and internal-only.

## Files

- `Chart.yaml`: chart metadata and any pinned upstream dependencies
- `values.yaml`: curated default values for CCF environments
- `questions.yaml`: catalog prompts exposed to operators
- `templates/NOTES.txt`: post-install guidance shown by Helm after install or upgrade

## References

- Source repository: `https://groundhog2k.github.io/helm-charts/`
- Project home: https://etcd.io/
- Release notes: https://github.com/etcd-io/etcd/releases
- Icon: https://raw.githubusercontent.com/cncf/artwork/master/projects/etcd/icon/color/etcd-icon-color.svg
