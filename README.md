# Public CCF Helm OCI Catalog

Public Helm OCI catalog source for Cloudera Cloud Factory.

This repository builds two catalog tracks:

- curated wrapper charts under `charts/` with CCF-oriented `values.yaml` and `questions.yaml`
- a mirrored copy of the published HelmForge catalog for additional community application coverage

## Curated Components

The curated catalog currently packages these components:

- `cert-manager`
- `external-dns`
- `istio`
- `harbor`
- `cloudnative-pg`
- `eck-operator`
- `eck-stack`
- `wordpress`
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
- `scripts/sync-helmforge.sh`: mirrors the full HelmForge catalog into OCI
- `scripts/validate_charts.py`: local Helm dependency, lint, template, and `questions.yaml` validation
- `scripts/validate-ccf-catalog.sh`: builds sharded CCF validation manifests for MCP-backed execution
- `docs/`: import, mirror, validation, and versioning guidance
- `.github/workflows/`: chart validation, publishing, mirroring, and update automation

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

Mirror a small HelmForge sample without pushing:

```bash
DRY_RUN=1 HELMFORGE_LIMIT=5 bash scripts/sync-helmforge.sh
```

## Publishing

Curated charts are intended to be pushed to:

```text
oci://ghcr.io/<owner>/ccf-charts
```

HelmForge mirror artifacts are intended to be pushed to:

```text
oci://ghcr.io/<owner>/helmforge-mirror
```

See `docs/ccf-import.md` for the CCF-side repository and catalog flow.
