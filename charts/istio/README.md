# ccf-istio

Curated `Istio` wrapper chart for the Cloudera Cloud Factory components catalog.

## Purpose

This chart packages upstream Helm dependencies with curated default values and a Rancher-style `questions.yaml` so it can be imported and installed more easily in CCF.

## Upstream Dependencies

- `base` from `https://istio-release.storage.googleapis.com/charts` at `1.29.2`
- `istiod` from `https://istio-release.storage.googleapis.com/charts` at `1.29.2`

## Defaults

- Namespace: `istio-system`
- Smoke profile: `default`
- Image source choice: `upstream-official`
- Chart version: `0.1.2`
- App version: `1.29.2`

## Notes

Official Istio control-plane wrapper combining the base and istiod charts.

## Files

- `Chart.yaml`: chart metadata and any pinned upstream dependencies
- `values.yaml`: curated default values for CCF environments
- `questions.yaml`: catalog prompts exposed to operators
- `templates/NOTES.txt`: post-install guidance shown by Helm after install or upgrade

## References

- Source repository: `https://istio-release.storage.googleapis.com/charts`
- Project home: https://istio.io
- Release notes: https://istio.io/latest/news/releases/
- Icon: https://istio.io/latest/favicons/android-192x192.png
