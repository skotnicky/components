# ccf-external-dns

Curated `external-dns` wrapper chart for the Cloudera Cloud Factory components catalog.

## Purpose

This chart packages upstream Helm dependencies with curated default values and a Rancher-style
`questions.yaml` so it can be imported and installed more easily in CCF.

## Upstream Dependencies

- `external-dns` from `https://kubernetes-sigs.github.io/external-dns/` at `1.20.0`

## Defaults

- Namespace: `external-dns`
- Smoke profile: `needs-overrides`
- Image source choice: `upstream-official`
- Chart version: `0.1.1`
- Upstream app version: `0.20.0`

## Notes

Official Kubernetes SIGs chart. Live validation usually needs provider-specific credentials and domain filters.

## Files

- `Chart.yaml`: wrapper metadata and pinned upstream dependencies
- `values.yaml`: curated default values for CCF environments
- `questions.yaml`: catalog prompts exposed to operators

## References

- Upstream repository: `https://kubernetes-sigs.github.io/external-dns/`
- Project home: https://github.com/kubernetes-sigs/external-dns/
- Icon: https://github.com/kubernetes-sigs/external-dns/raw/master/docs/img/external-dns.png
