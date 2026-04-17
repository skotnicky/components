# Catalog Matrix

Generated from `scripts/catalog_data.py` to keep the curated catalog, validation, and automation flows aligned.

## Curated Wrappers And Exclusions

| Component | Packaged Chart | Upstream Source | Version | Namespace | Classification | Packaging | Questions | Smoke Profile | Images | Notes |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| cert-manager | ccf-cert-manager | `https://charts.jetstack.io` | v1.20.2 | `cert-manager` | official | curated-wrapper | yes | default | upstream-official | Official Jetstack chart with lightweight monitoring defaults for CCF projects. |
| external-dns | ccf-external-dns | `https://kubernetes-sigs.github.io/external-dns/` | 1.20.0 | `external-dns` | official | curated-wrapper | yes | needs-overrides | upstream-official | Official Kubernetes SIGs chart. Live validation usually needs provider-specific credentials and domain filters. |
| istio | ccf-istio | `https://istio-release.storage.googleapis.com/charts` | 1.29.2 | `istio-system` | official | curated-wrapper | yes | default | upstream-official | Official Istio control-plane wrapper combining the base and istiod charts. |
| harbor | ccf-harbor | `https://helm.goharbor.io` | 1.18.3 | `harbor` | official | curated-wrapper | yes | needs-overrides | upstream-official | Official Harbor chart. Initial defaults keep upstream images because Harbor ships multiple tightly coupled components. |
| cloudnative-pg | ccf-cloudnative-pg | `https://cloudnative-pg.github.io/charts` | 0.28.0 | `cnpg-system` | official | curated-wrapper | yes | default | upstream-official | Namespace-scoped operator defaults are used for safer CCF project installs. |
| eck-operator | ccf-eck-operator | `https://helm.elastic.co` | 3.3.2 | `elastic-system` | official | curated-wrapper | yes | default | upstream-official | Elastic's operator is packaged separately so the stack chart can be validated after it. |
| eck-stack | ccf-eck-stack | `https://helm.elastic.co` | 0.18.2 | `elastic-stack` | official | curated-wrapper | yes | needs-overrides | upstream-official | Validated only after the ECK operator is installed. The default profile keeps the stack small and enables Elasticsearch plus Kibana. |
| wordpress | ccf-wordpress | `https://repo.helmforge.dev` | 1.4.7 | `wordpress` | community | curated-wrapper | yes | needs-overrides | upstream-official | HelmForge is used here to satisfy the non-Bitnami WordPress requirement. |
| grafana | ccf-grafana | `https://grafana.github.io/helm-charts` | 10.5.15 | `grafana` | official | curated-wrapper | yes | default | upstream-official | Initial defaults remain close to upstream and keep ingress off by default. |
| jupyterhub | ccf-jupyterhub | `https://hub.jupyter.org/helm-chart/` | 4.3.3 | `jupyterhub` | official | curated-wrapper | yes | needs-overrides | upstream-official | Proxy service is normalized to ClusterIP to fit most CCF projects. |
| ollama | ccf-ollama | `https://helm.otwld.com/` | 1.54.0 | `ollama` | community | curated-wrapper | yes | needs-overrides | upstream-official | Community chart. Default profile keeps networking internal and persistence enabled. |
| backstage | ccf-backstage | `https://backstage.github.io/charts` | 2.6.3 | `backstage` | official | curated-wrapper | yes | manual-only | upstream-official | The official chart currently depends on Bitnami common/postgresql artifacts. This wrapper keeps postgresql disabled by default and marks validation manual-only. |
| trino | ccf-trino | `https://trinodb.github.io/charts/` | 1.42.1 | `trino` | official | curated-wrapper | yes | default | upstream-official | Internal-only service defaults keep Trino easy to validate inside a project. |
| clickhouse-operator | ccf-clickhouse-operator | `oci://ghcr.io/clickhouse` | 0.0.3 | `clickhouse-operator` | official | curated-wrapper | yes | default | upstream-official | Official ClickHouse operator chart from GHCR OCI. |
| valkey | ccf-valkey | `https://valkey.io/valkey-helm/` | 0.9.4 | `valkey` | official | curated-wrapper | yes | default | upstream-official | Official Valkey chart with conservative single-primary defaults. |
| openmetadata | ccf-openmetadata | `https://helm.open-metadata.org/` | 1.12.5 | `openmetadata` | official | curated-wrapper | yes | manual-only | upstream-official | The application chart expects external database and search services for a clean non-Bitnami setup. Validation remains manual-only until those overrides are supplied. |
| netbox | ccf-netbox | `https://charts.netbox.oss.netboxlabs.com/` | 8.1.1 | `netbox` | community | curated-wrapper | yes | manual-only | upstream-official | The community chart currently depends on Bitnami common/postgresql/valkey artifacts. Validation remains manual-only while external service wiring is supplied. |
| chaos-mesh | ccf-chaos-mesh | `https://charts.chaos-mesh.org` | 2.8.2 | `chaos-mesh` | official | curated-wrapper | yes | needs-overrides | upstream-official | Dashboard is normalized to ClusterIP instead of the upstream NodePort default. |
| memcached | excluded | `n/a` | n/a | `n/a` | excluded | excluded | no | manual-only | n/a | No maintained official or community Helm chart could be validated outside archived charts or Bitnami. |

## HelmForge Mirror

- Source classification: `community`
- Packaging mode: `helmforge-mirror`
- Questions support: `no`
- Upstream repository: `https://repo.helmforge.dev`
- OCI destination prefix: `oci://ghcr.io/<owner>/helmforge-mirror`
- Requested component coverage via mirror: `rabbitmq`, `elasticsearch`, `wordpress`
- Notes: Mirror all published HelmForge packages into a dedicated OCI namespace. Validation is sharded because the upstream catalog changes over time.

## Explicit Exclusions

- `memcached`: No maintained official or community Helm chart could be validated outside archived charts or Bitnami.
