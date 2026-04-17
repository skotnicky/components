# Public CCF Helm OCI Catalog

Public Helm OCI catalog source for Cloudera Cloud Factory.

This repository builds curated wrapper charts under `charts/` with CCF-oriented `values.yaml`
and `questions.yaml`.

## Curated Components

The curated catalog currently packages these components:

- `cert-manager`
- `external-dns`
- `istio`
- `harbor`
- `cloudnative-pg`
- `eck-operator`
- `eck-stack`
- `grafana`
- `jupyterhub`
- `ollama`
- `backstage`
- `trino`
- `clickhouse-operator`
- `valkey`
- `openmetadata`
- `netbox`
- `chaos-mesh`

The generated compatibility matrix lives in `docs/catalog-matrix.md`.

## Repository Layout

- `charts/`: generated curated wrapper charts
- `scripts/catalog_data.py`: single source of truth for curated chart metadata
- `scripts/render_catalog.py`: regenerates charts and the catalog matrix
- `scripts/build_helm_repo.sh`: packages curated charts and generates a classic Helm repo with `index.yaml`
- `scripts/validate_charts.py`: local Helm dependency, lint, template, and `questions.yaml` validation
- `scripts/validate-ccf-catalog.sh`: builds sharded CCF validation manifests for MCP-backed execution
- `docs/`: import, validation, and versioning guidance
- `.github/workflows/`: chart validation, publishing, and update automation

## Local Development

Install Python dependencies first:

```bash
python3 -m pip install -r requirements.txt
```

Regenerate the curated charts and matrix:

```bash
python3 scripts/render_catalog.py
```

Run local chart validation:

```bash
python3 scripts/validate_charts.py
```

Build a sample CCF validation manifest:

```bash
bash scripts/validate-ccf-catalog.sh
```

Build a classic Helm repository locally:

```bash
HELM_REPO_URL=https://example.github.io/components \
bash scripts/build_helm_repo.sh
```

## Publishing

Curated charts are intended to be pushed to:

```text
oci://ghcr.io/<owner>/ccf-charts
```

The classic Helm repository published by GitHub Pages is intended to be available at:

```text
https://<owner>.github.io/<repo>/
```

The Pages artifact includes:

- `index.yaml` for Helm and CCF consumers
- a minimal `index.html` landing page at the repository root

Set the optional repository variable `HELM_REPO_URL` if you want Pages to publish a custom repository base URL into `index.yaml`.

External community repositories that are not curated here can be added directly to CCF from
their upstream sources.

See `docs/ccf-import.md` for the CCF-side repository and catalog flow.
