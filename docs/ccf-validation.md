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
- `scripts/probe_question_types_mcp.py`

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
- generated Helm NOTES show a concrete access URL when the chart exposes `externalURL` or ingress
  hostname data
- known bootstrap endpoints respond when the chart exposes them

Smoke tests intentionally stop short of deep product-specific workflows.

The kubeconfig helper currently focuses on:

- cluster access preflight through `kubectl auth can-i`
- workload readiness for Deployments, StatefulSets, DaemonSets, and Jobs
- pod health checks, including common crash loop/image pull failures
- namespace-level service, endpoint, ingress, and PVC inventory
- namespace deletion and residual-resource verification during cleanup

## Question Transport

Live validation uses CCF application parameters only for question types that reliably survive the
current transport path. In practice, local validation automation now treats `string`, `enum`,
`boolean`, and `int` prompts as safe non-indexed app parameters.

Current reliable transport path:

- strings: passed directly as app parameters
- enums: passed directly as app parameters
- booleans: passed through CCF app parameters as typed values
- integers: passed through CCF app parameters as typed values
- list-like values: modeled as indexed `string` prompts where practical because native
  `listofstrings` questions are not preserved by CCF; indexed paths stay out of generated
  `questionParameters`

Observed live behavior:

- the live question probe confirmed that `string`, `enum`, `boolean`, and `int` survive the CCF
  app-parameter path
- the same probe confirmed native `listofstrings` questions are not preserved, so the curated
  catalog now uses indexed `string` prompts for list-style operator input where practical
- `grafana` installed successfully with string/enum-style defaults applied through app parameters
- `cloudnative-pg` and similar charts can now keep boolean/integer prompts in the safe
  app-parameter set
- `cert-manager` may still fail in clusters with pre-existing CRDs owned by an older Helm release,
  but that is now separate from question-type transport
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
- native list-question transport remains a platform limitation, so list-style prompts still cannot
  be treated as safe direct install-time overrides through generated `questionParameters`

## MCP Question Probe

The repository now includes `scripts/probe_question_types_mcp.py` for question-transport checks
against the standalone `ccf-question-types-smoke` chart using the same MCP-runner path as the rest
of local CCF validation. Indexed list-slot questions are skipped because the generated validation
manifest intentionally excludes indexed paths from automatic app-parameter injection.

The probe:

1. builds one single-app manifest per supported non-indexed question plus a baseline manifest
2. overrides exactly one parameter in each manifest
3. writes the case manifests under `reports/question-types-mcp-cases/`
4. optionally runs `scripts/validate-ccf-app.sh` for each case when `--run` is supplied
5. relies on the existing `MCP_RUNNER_CMD` hook to execute the live CCF MCP lifecycle
6. collects per-case runner exit codes and stdout/stderr into a JSON report

Example:

```bash
MCP_RUNNER_CMD='your-local-mcp-runner' \
python3 scripts/probe_question_types_mcp.py \
  --repository-name ccf \
  --run
```

Without `--run`, the script only prepares the per-case manifests so they can be executed or
inspected manually. The summary report is written to `reports/question-types-mcp-probe.json` by
default.

## Sharding

Curated validation can still be sharded to shorten the total runtime.

Recommended approach:

- shard by curated chart index modulo shard count

## Manual-Only Profiles

Some curated charts are still marked `manual-only` in the catalog matrix because they depend on
project-specific external services or heavier stateful tuning that the default automation does not
yet provide:

- `backstage`: now packaged as a standalone in-repo chart, but still expects an external PostgreSQL
  service such as a CloudNativePG-managed database
- `mysql`: stateful backend chart intended as a companion service for apps such as OpenMetadata
- `netbox`: now packaged as a standalone in-repo chart, but still expects external PostgreSQL and
  Valkey services
- `openmetadata`: still expects external MySQL and OpenSearch wiring even though the app chart
  itself no longer inherits Bitnami dependencies
- `opensearch`: stateful backend chart intended as a companion service for apps such as
  OpenMetadata

Those charts should remain visible in the catalog, but automated CCF smoke validation should still
treat them as exceptions until the external-service provisioning story is automated further.
