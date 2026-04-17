# CCF Import Flow

This repository is designed for Cloudera Cloud Factory repository import and catalog curation.

## OCI Repositories

Import two OCI repositories into CCF:

- curated wrappers: `oci://ghcr.io/<owner>/ccf-charts`
- HelmForge mirror: `oci://ghcr.io/<owner>/helmforge-mirror`

## Expected CCF Flow

1. Import the OCI repository into CCF.
2. Create or select a catalog.
3. Bind curated applications or mirrored HelmForge applications into that catalog.
4. Bind projects to the catalog.
5. Install application instances into target namespaces.

The CCF MCP server exposes that same sequence through:

- `import-repository`
- `catalog-create`
- `catalog-app-add`
- `catalog-app-defaults-set`
- `bind-projects-to-catalog`
- `app-install`

## Curated Defaults

Curated wrapper charts carry two configuration layers:

- `values.yaml`: safe default values intended to install on a typical CCF Kubernetes project
- `questions.yaml`: operator-facing prompts for the values most likely to vary between organizations

Typical curated questions cover:

- ingress enablement, class, and hostname
- service type
- storage class and PVC size
- lightweight resource settings
- bootstrap admin or secret references when the upstream chart supports them

## Catalog Strategy

Recommended split:

- one curated catalog sourced from `ccf-charts`
- one community catalog sourced from `helmforge-mirror`

That keeps lifecycle expectations separate while still making both catalogs available to every organization.

## Notes On Coverage

- `rabbitmq` is covered through the HelmForge mirror
- `memcached` is still not supported because no maintained non-Bitnami source was validated
- some curated upstream charts still require manual review because their upstream ecosystem references Bitnami helper dependencies even when the deployed images are not Bitnami-based
