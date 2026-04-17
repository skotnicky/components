# ccf-eck-stack

Curated `Elastic ECK Stack` wrapper chart for the Cloudera Cloud Factory components catalog.

## Purpose

This chart packages upstream Helm dependencies with curated default values and a Rancher-style
`questions.yaml` so it can be imported and installed more easily in CCF.

## Upstream Dependencies

- `eck-stack` from `https://helm.elastic.co` at `0.18.2`

## Defaults

- Namespace: `elastic-stack`
- Smoke profile: `needs-overrides`
- Image source choice: `upstream-official`
- Chart version: `0.1.2`
- Upstream app version: `0.18.2`

## Notes

Validated only after the ECK operator is installed. The default profile keeps the stack small and enables Elasticsearch plus Kibana.

## Files

- `Chart.yaml`: wrapper metadata and pinned upstream dependencies
- `values.yaml`: curated default values for CCF environments
- `questions.yaml`: catalog prompts exposed to operators

## References

- Upstream repository: `https://helm.elastic.co`
- Project home: https://github.com/elastic/cloud-on-k8s
- Icon: https://helm.elastic.co/icons/eck.png
