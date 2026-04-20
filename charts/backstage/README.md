# ccf-backstage

Curated `Backstage` standalone chart for the Cloudera Cloud Factory components catalog.

## Purpose

This chart is maintained directly in this repository so Backstage can be installed without depending on upstream Bitnami-backed PostgreSQL chart packaging.

## Upstream Dependencies

This chart has no external Helm dependencies.

## Defaults

- Namespace: `backstage`
- Smoke profile: `manual-only`
- Image source choice: `upstream-official`
- Chart version: `0.1.2`
- App version: `latest`

## Notes

Standalone curated chart that removes the upstream Bitnami-backed dependency path and expects an external PostgreSQL service such as a CloudNativePG-managed database.

## Files

- `Chart.yaml`: chart metadata and any pinned upstream dependencies
- `values.yaml`: curated default values for CCF environments
- `questions.yaml`: catalog prompts exposed to operators
- `templates/NOTES.txt`: post-install guidance shown by Helm after install or upgrade

## References

- Source repository: `local://components/backstage`
- Project home: https://backstage.io
- Release notes: https://github.com/backstage/backstage/releases
- Icon: https://raw.githubusercontent.com/cncf/artwork/master/projects/backstage/icon/color/backstage-icon-color.svg
