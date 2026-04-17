# CCF Validation

CCF validation is split into two layers:

- local repository validation in GitHub Actions for chart integrity
- live deployment validation against CCF using the Cloudera Cloud Factory MCP server

## Local Validation

Local validation is fully repository-driven:

- `helm dependency build`
- `helm lint`
- `helm template`
- `questions.yaml` path checks
- HelmForge mirror inventory and integrity checks

## Live CCF Validation

Live validation uses the CCF MCP server rather than `taikun-cli`.

The repository prepares sharded validation manifests through:

- `scripts/build_validation_manifest.py`
- `scripts/validate-ccf-catalog.sh`
- `scripts/validate-ccf-app.sh`

The expected execution environment is a self-hosted automation runner with:

- repository checkout
- Helm and Python available
- access to the CCF MCP server
- an `MCP_RUNNER_CMD` hook that consumes shard or app manifests and performs the live CCF actions

## Validation Sequence

For each curated chart and each mirrored HelmForge chart:

1. ensure the source repository is imported into CCF
2. ensure the application exists in the validation catalog
3. install the app into a dedicated validation namespace
4. wait for Ready state
5. run basic smoke checks
6. uninstall the app
7. verify cleanup before moving on

## Basic Smoke Checks

Basic functionality means:

- pods become healthy
- services and endpoints are present
- ingress objects exist when enabled
- known bootstrap endpoints respond when the chart exposes them

Smoke tests intentionally stop short of deep product-specific workflows.

## Sharding

The full HelmForge catalog is large enough that validation should be sharded.

Recommended approach:

- shard by chart index modulo shard count
- keep curated charts on shard `0`
- distribute mirrored HelmForge charts across all shards

## Manual-Only Profiles

Some curated charts are currently marked `manual-only` in the catalog matrix because their upstream chart ecosystems still require manual overrides or non-trivial external services:

- `backstage`
- `openmetadata`
- `netbox`

Those charts should remain visible in the catalog, but automated CCF smoke validation should treat them as exceptions until a clean non-Bitnami dependency path is available.
