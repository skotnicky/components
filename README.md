# Public CCF Helm OCI Catalog

Public Helm OCI catalog source for Cloudera Cloud Factory.

This repository builds curated wrapper and standalone charts under `charts/` with CCF-oriented
`values.yaml` and `questions.yaml`, annotated `Chart.yaml` metadata, and generated Helm
`templates/NOTES.txt` guidance.

## Curated Components

The curated catalog currently packages these components:

- `istio`
- `harbor`
- `cloudnative-pg`
- `mysql`
- `minio-operator`
- `etcd`
- `milvus`
- `eck-operator`
- `eck-stack`
- `grafana`
- `jupyterhub`
- `ollama`
- `backstage`
- `trino`
- `superset`
- `dify`
- `clickhouse-operator`
- `valkey`
- `opensearch`
- `openmetadata`
- `netbox`
- `chaos-mesh`

The generated compatibility matrix lives in `docs/catalog-matrix.md`.

Most catalog entries still wrap pinned upstream charts. `backstage` and `netbox` are now maintained
as standalone in-repo charts so they no longer inherit upstream Bitnami-backed PostgreSQL/Valkey
subcharts, while `mysql` and `opensearch` are curated non-Bitnami backend companions for external
service flows such as OpenMetadata.

## Repository Layout

- `charts/`: generated curated charts plus any in-repo templates/files for standalone entries
- `scripts/catalog_data.py`: single source of truth for curated chart metadata
- `scripts/catalog_state.json`: machine-managed pinned upstream versions and curated chart versions
- `scripts/render_catalog.py`: regenerates charts and the catalog matrix
- `scripts/build_helm_repo.sh`: packages curated charts and generates a classic Helm repo with `index.yaml`
- `scripts/validate_charts.py`: local Helm dependency, lint, template, and `questions.yaml` validation
- `scripts/validate-ccf-catalog.sh`: builds sharded CCF validation manifests for MCP-backed execution
- `scripts/validate_k8s_resources.py`: kubeconfig-backed smoke checks and cleanup helpers for live validation
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

This only prepares manifests unless you run it locally with MCP access.

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
- previously released chart archives preserved for append-only version history

Set the optional repository variable `HELM_REPO_URL` if you want Pages to publish a custom repository base URL into `index.yaml`.

## Update Automation

The scheduled update workflow:

- checks curated upstream chart sources for new releases
- writes new pinned upstream versions into `scripts/catalog_state.json`
- bumps the curated wrapper chart version instead of replacing an existing release
- opens a pull request and enables auto-merge after required checks pass

If you want the automation PR to trigger normal pull-request checks reliably, configure a
repository secret named `CATALOG_UPDATE_TOKEN` with permission to create branches and pull
requests. The workflow falls back to `GITHUB_TOKEN`, but GitHub may suppress downstream workflow
triggers for PRs created by that token.

Enable GitHub repository auto-merge in the repository settings so the scheduled update PR can merge
itself after the required checks succeed.

## Question Parameters

Generated `questions.yaml` files remain the source of truth for operator prompts. Live CCF
validation now injects `string`, `enum`, `boolean`, and `int` values through app parameters for
non-indexed question paths. Native list questions are still not preserved by CCF, so curated charts
model list-like operator input as indexed `string` prompts where practical.

Current live-validation normalization uses:

- direct strings for string questions
- direct strings for enum questions
- typed boolean parameters for boolean questions
- typed integer parameters for int questions
- indexed string prompts for list-like values when a chart needs operator-visible list slots

Indexed list prompts remain excluded from automated app-parameter injection and are intended for UI
or manual override flows instead.

Current live validation in CCF also supports:

- removing chart packages from temporary catalogs after each run
- deleting leftover namespaces and namespaced Kubernetes resources through the MCP Kubernetes tools
- validating cluster access, smoke-checking workloads, and deleting namespaces through kubeconfig-backed `kubectl`
- querying project logs and Prometheus metrics through local MCP tools when monitoring is enabled

The preferred live-validation mode is now hybrid:

- use CCF MCP for catalog and application lifecycle
- use kubeconfig plus `kubectl` for Kubernetes inspection and cleanup

Live CCF validation is intended to run only on your local computer. GitHub workflows in this
repository prepare manifests and other repo artifacts, but they do not call the MCP server.

Validation manifests now include both:

- `kubernetesValidation` hints for kubeconfig-backed checks
- `observabilityValidation` hints for local MCP log and metric queries

When running `scripts/validate-ccf-catalog.sh` or `scripts/validate-ccf-app.sh`, set:

```bash
VALIDATION_USE_KUBECTL=1
VALIDATION_KUBECONFIG_PATH=/absolute/path/to/kubeconfig.yaml
```

The kubeconfig itself can be created through the CCF MCP `create-kubeconfig` tool and then retrieved with `get-kubeconfig`.

## Managed DNS And Certificates

CCF projects can enable a managed DNS/Cert service through the platform API
(`/api/v1/dns-cert/enable`). The service is based on `external-dns` and `cert-manager`:
when enabled, the platform runs both controllers inside the project and provisions a
default cluster-scoped issuer named `ccf-default` (Let's Encrypt by default) plus a
managed DNS domain.

Every ingress-capable curated chart is wired to use that service by default. The shared
metadata in `scripts/catalog_data.py` (`INGRESS_CAPABILITIES` plus
`apply_dns_cert_defaults`) adds, for each such chart:

- ingress annotations `cert-manager.io/cluster-issuer: ccf-default` and
  `external-dns.alpha.kubernetes.io/ttl` so cert-manager's ingress-shim issues a
  certificate and external-dns publishes the record
- a curated TLS block that stores the issued certificate in a `<component>-tls` secret

Because `external-dns` reads the ingress hosts directly, exposing a chart with a hostname
inside the project's managed DNS domain is enough to get a public DNS record and a valid
TLS certificate with no extra per-chart wiring. Ingress stays disabled by default, so
these defaults are inert until an operator enables the ingress, and the annotations are
harmless on projects that do not run the managed service.

When adding a new ingress-capable chart, set its `annotations_path` (and, where the
upstream TLS shape differs, `tls_secret_path`/`tls_extra`) in `INGRESS_CAPABILITIES`
rather than hand-editing generated values. The managed issuer name and annotation keys
are defined once as `CCF_DNS_CERT_CLUSTER_ISSUER` and related constants.

## NOTES And Access URLs

Generated `templates/NOTES.txt` files now do two things:

- surface source, home, and release-notes links from shared chart metadata
- print a concrete access URL when a chart exposes enough data to derive one from `externalURL` or
  ingress host values

The shared ingress metadata in `scripts/catalog_data.py` is the source of truth for those NOTES URL
snippets. When adding a new ingress-capable chart, update that metadata rather than hand-editing a
chart-specific NOTES template.

External community repositories that are not curated here can be added directly to CCF from
their upstream sources.

See `docs/ccf-import.md` for the CCF-side repository and catalog flow.
