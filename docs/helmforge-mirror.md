# HelmForge Mirror

This repository mirrors the published HelmForge chart catalog into a dedicated OCI namespace so CCF can consume HelmForge packages through the same GitHub Container Registry footprint as the curated charts.

## Source And Destination

- source repository: `https://repo.helmforge.dev`
- destination OCI prefix: `oci://ghcr.io/<owner>/helmforge-mirror`

The mirror keeps upstream chart versions intact and records:

- chart name
- chart version
- app version
- source digest from the Helm repository index
- local archive SHA256

## Mirror Script

Use the mirror script directly:

```bash
OCI_PREFIX="oci://ghcr.io/<owner>/helmforge-mirror" \
bash scripts/sync-helmforge.sh
```

Useful environment variables:

- `DRY_RUN=1`: download and inventory charts without pushing to OCI
- `HELMFORGE_LIMIT=25`: limit the number of mirrored charts for testing
- `HELMFORGE_FILTER_REGEX='^(wordpress|rabbitmq)$'`: mirror only a subset of charts
- `REPORT_PATH=reports/helmforge-mirror-manifest.json`: customize the output manifest path

## Requested Component Coverage

The live HelmForge catalog currently covers these requested components:

- `wordpress`
- `rabbitmq`
- `elasticsearch`

That means `rabbitmq` is available through the HelmForge mirror even though this repo does not maintain a first-party curated wrapper chart for it.

## Operational Notes

- mirror validation should be sharded for CCF smoke tests because the upstream catalog size changes over time
- mirror publication should run on schedule and on manual dispatch
- any chart absent from HelmForge should not be inferred as supported by the mirror
