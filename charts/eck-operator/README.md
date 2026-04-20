# ccf-eck-operator

Curated `Elastic ECK Operator` wrapper chart for the Cloudera Cloud Factory components catalog.

## Purpose

This chart packages upstream Helm dependencies with curated default values and a Rancher-style `questions.yaml` so it can be imported and installed more easily in CCF.

## Upstream Dependencies

- `eck-operator` from `https://helm.elastic.co` at `3.3.2`

## Defaults

- Namespace: `elastic-system`
- Smoke profile: `default`
- Image source choice: `upstream-official`
- Chart version: `0.1.2`
- App version: `3.3.2`

## Notes

Elastic's operator is packaged separately so the stack chart can be validated after it.

## Files

- `Chart.yaml`: chart metadata and any pinned upstream dependencies
- `values.yaml`: curated default values for CCF environments
- `questions.yaml`: catalog prompts exposed to operators
- `templates/NOTES.txt`: post-install guidance shown by Helm after install or upgrade

## References

- Source repository: `https://helm.elastic.co`
- Project home: https://github.com/elastic/cloud-on-k8s
- Release notes: https://github.com/elastic/cloud-on-k8s/releases
- Icon: https://helm.elastic.co/icons/eck.png
