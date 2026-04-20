# ccf-cert-manager

Curated `cert-manager` wrapper chart for the Cloudera Cloud Factory components catalog.

## Purpose

This chart packages upstream Helm dependencies with curated default values and a Rancher-style `questions.yaml` so it can be imported and installed more easily in CCF.

## Upstream Dependencies

- `cert-manager` from `https://charts.jetstack.io` at `v1.20.2`

## Defaults

- Namespace: `cert-manager`
- Smoke profile: `default`
- Image source choice: `upstream-official`
- Chart version: `0.1.2`
- App version: `v1.20.2`

## Notes

Official Jetstack chart with lightweight monitoring defaults for CCF projects.

## Files

- `Chart.yaml`: chart metadata and any pinned upstream dependencies
- `values.yaml`: curated default values for CCF environments
- `questions.yaml`: catalog prompts exposed to operators

## References

- Source repository: `https://charts.jetstack.io`
- Project home: https://cert-manager.io
- Icon: https://raw.githubusercontent.com/cert-manager/community/4d35a69437d21b76322157e6284be4cd64e6d2b7/logo/logo-small.png
