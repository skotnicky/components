# ccf-backstage

Curated `Backstage` wrapper chart for the Cloudera Cloud Factory components catalog.

## Purpose

This chart packages upstream Helm dependencies with curated default values and a Rancher-style `questions.yaml` so it can be imported and installed more easily in CCF.

## Upstream Dependencies

- `backstage` from `https://backstage.github.io/charts` at `2.6.3`

## Defaults

- Namespace: `backstage`
- Smoke profile: `manual-only`
- Image source choice: `upstream-official`
- Chart version: `0.1.2`
- App version: `2.6.3`

## Notes

The official chart currently depends on Bitnami common/postgresql artifacts. This wrapper keeps postgresql disabled by default and marks validation manual-only.

## Files

- `Chart.yaml`: chart metadata and any pinned upstream dependencies
- `values.yaml`: curated default values for CCF environments
- `questions.yaml`: catalog prompts exposed to operators

## References

- Source repository: `https://backstage.github.io/charts`
- Project home: https://backstage.io
- Icon: https://raw.githubusercontent.com/cncf/artwork/master/projects/backstage/icon/color/backstage-icon-color.svg
