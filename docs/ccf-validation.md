# CCF Validation

CCF validation is split into two layers:

- local repository validation in GitHub Actions for chart integrity
- live deployment validation on your local computer using the Cloudera Cloud Factory MCP server plus project kubeconfig access

## Local Validation

Local validation is fully repository-driven:

- `helm dependency build`
- `helm lint`
- `helm template`
- `questions.yaml` path checks

## Live CCF Validation

Live validation uses the CCF MCP server rather than `taikun-cli`, and should also use a
project-scoped kubeconfig for direct Kubernetes checks.

GitHub Actions should not call the CCF MCP server. In this repository, GitHub only prepares
validation manifests and uploads them as artifacts. Actual CCF lifecycle calls and kubeconfig-based
cluster checks are intended to run locally on your machine.

The repository prepares sharded validation manifests through:

- `scripts/build_validation_manifest.py`
- `scripts/validate-ccf-catalog.sh`
- `scripts/validate-ccf-app.sh`

The expected execution environment for live validation is your local workstation with:

- repository checkout
- Helm and Python available
- `kubectl` available
- access to the CCF MCP server
- either direct MCP tool access or an `MCP_RUNNER_CMD` hook that consumes shard or app manifests
- a kubeconfig created with the CCF MCP `create-kubeconfig` tool and retrieved with `get-kubeconfig`

The GitHub workflow under `.github/workflows/validate-ccf.yml` is limited to manifest preparation.
It does not set `MCP_RUNNER_CMD`, does not create kubeconfigs, and does not execute live CCF
operations.

In local runs, the same flow can be executed directly with the CCF MCP tools for:

- catalog creation
- catalog app add/defaults set/remove
- project binding
- app install / wait / uninstall
- catalog unbind / catalog cleanup
- Kubernetes namespace and resource inspection/deletion

The preferred hybrid split is:

- MCP tools: catalog creation, catalog app add/defaults set/remove, project binding, app install,
  wait, uninstall, and catalog cleanup
- kubeconfig plus `kubectl`: context validation, workload/pod/service inspection, and namespace
  deletion when uninstall leaves namespaced resources behind

The repository now provides `scripts/validate_k8s_resources.py` for the kubeconfig-backed part of
that flow. The generated validation manifests include a `kubernetesValidation` block so the MCP
runner can call the helper script during smoke and cleanup phases.

The generated validation manifests now also include an `observabilityValidation` block for local
MCP-based diagnosis. It points at the MCP tools:

- `autocomplete-project-metrics`
- `query-project-prometheus-metrics`
- `query-project-loki-logs`
- `export-project-loki-logs`

Typical split:

- GitHub Actions: generate and upload sharded validation manifests
- local computer: call MCP tools, install apps, wait for readiness, run smoke checks, and clean up

## Observability Checks

When project monitoring is enabled, local validation can collect extra evidence through MCP:

- Loki logs scoped to the target namespace
- Prometheus metrics scoped to the target namespace
- exported log payloads for deeper post-failure analysis

The default manifest hints currently suggest:

- Loki query: `{namespace="<target-namespace>"}`
- Prometheus namespace health: `kube_namespace_status_phase{namespace="<target-namespace>",phase="Active"}`
- Prometheus ready pod count: `sum(kube_pod_status_ready{namespace="<target-namespace>",condition="true"})`
- Prometheus service count: `count(kube_service_info{namespace="<target-namespace>"})`
- Prometheus container restart count: `sum(kube_pod_container_status_restarts_total{namespace="<target-namespace>"})`

These observability queries should remain local-only, alongside the rest of the MCP flow.

## Validation Sequence

For each curated chart:

1. ensure the source repository is imported into CCF
2. ensure the application exists in the validation catalog
3. install the app into a dedicated validation namespace
4. wait for Ready state
5. run basic smoke checks
6. uninstall the app
7. verify cleanup before moving on

In practice, use one temporary catalog per chart and the same target project. A successful cleanup
cycle means:

- the project app is deleted
- the catalog app is removed from the temporary catalog
- the project is unbound from the temporary catalog
- the temporary catalog is deleted
- any leftover namespaces or namespaced resources are deleted through kubeconfig-backed `kubectl`
  or the Kubernetes resource MCP tools

## Basic Smoke Checks

Basic functionality means:

- pods become healthy
- services and endpoints are present
- ingress objects exist when enabled
- known bootstrap endpoints respond when the chart exposes them

Smoke tests intentionally stop short of deep product-specific workflows.

The kubeconfig helper currently focuses on:

- cluster access preflight through `kubectl auth can-i`
- workload readiness for Deployments, StatefulSets, DaemonSets, and Jobs
- pod health checks, including common crash loop/image pull failures
- namespace-level service, endpoint, ingress, and PVC inventory
- namespace deletion and residual-resource verification during cleanup

## Question Transport

Live validation uses CCF application parameters for generated `questions.yaml` prompts. Boolean,
integer, and list-style defaults should stay available to operators; validation tooling must
normalize those values into the form CCF expects before sending them through the install path.

Observed normalization rules:

- booleans: lowercase YAML booleans such as `true` and `false`
- integers: plain decimal strings such as `30`
- list of strings: JSON array strings such as `["service", "ingress"]`

Observed live behavior:

- normalized boolean/string/enum question defaults worked for `grafana`
- normalized boolean/string/enum question defaults also progressed cleanly for `cloudnative-pg`
- `cert-manager` no longer failed on schema typing after normalization; the remaining failure came
  from pre-existing CRDs owned by an older Helm release in the target cluster
- `grafana` installed successfully, reached `Ready`, uninstalled, and its leftover namespace could
  be removed through the Kubernetes resource MCP tools
- a project kubeconfig could be created through MCP and used successfully for cluster-wide reads,
  permission checks, and namespace create/delete probes
- project monitoring is now enabled on `awc-test`, and the new Loki/Prometheus MCP tools returned
  live data successfully during validation exploration

## Current Gaps

- cluster-scoped cleanup is still limited in practice: although CRDs can be described, the current
  delete-resource endpoint rejected `Crd` deletions during live validation
- some list endpoints are more reliable for Namespaces, Deployments, and Services than for Pods,
  so smoke checks should prefer stable kinds first and fall back to app-level status when needed
- the repository can now hand hybrid validation metadata to an MCP runner, but the external runner
  still needs to invoke `scripts/validate_k8s_resources.py` at the appropriate smoke and cleanup
  points
- the repo now carries observability hints, but local automation still needs to decide exactly when
  to query logs and metrics during install failures or post-ready smoke checks

## Sharding

Curated validation can still be sharded to shorten the total runtime.

Recommended approach:

- shard by curated chart index modulo shard count

## Manual-Only Profiles

Some curated charts are currently marked `manual-only` in the catalog matrix because their upstream chart ecosystems still require manual overrides or non-trivial external services:

- `backstage`
- `openmetadata`
- `netbox`

Those charts should remain visible in the catalog, but automated CCF smoke validation should treat them as exceptions until a clean non-Bitnami dependency path is available.
