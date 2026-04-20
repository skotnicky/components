"""Shared catalog metadata for curated CCF charts."""

from copy import deepcopy
import json
import os
import pathlib
import subprocess


def q(variable, label, qtype, default, description, group, options=None, required=False):
    item = {
        "variable": variable,
        "label": label,
        "type": qtype,
        "default": default,
        "description": description,
        "group": group,
        "required": required,
    }
    if options:
        item["options"] = options
    return item


def primary_dependency(component: dict) -> dict | None:
    dependencies = component.get("dependencies", [])
    return dependencies[0] if dependencies else None


def component_source_repository(component: dict) -> str:
    dep = primary_dependency(component)
    if dep:
        return dep["repository"]
    return component.get("source_repository", "local://standalone")


def component_app_version(component: dict) -> str:
    dep = primary_dependency(component)
    if dep:
        return dep.get("app_version") or dep["version"]
    return component.get("app_version", component.get("chart_version", DEFAULT_CHART_VERSION))


def parse_path(path: str) -> list[str]:
    parts = []
    for chunk in path.split("."):
        while "[" in chunk:
            prefix, rest = chunk.split("[", 1)
            if prefix:
                parts.append(prefix)
            index, chunk = rest.split("]", 1)
            parts.append(index)
        if chunk:
            parts.append(chunk)
    return parts


def set_path_default(data: dict, path: str, value) -> None:
    cur = data
    parts = parse_path(path)
    for idx, part in enumerate(parts):
        is_last = idx == len(parts) - 1
        next_part = parts[idx + 1] if not is_last else None
        if isinstance(cur, list):
            list_index = int(part)
            while len(cur) <= list_index:
                cur.append({} if next_part and not next_part.isdigit() else [])
            if is_last:
                if cur[list_index] in ({}, None, ""):
                    cur[list_index] = value
                return
            if cur[list_index] in ({}, None, ""):
                cur[list_index] = {} if next_part and not next_part.isdigit() else []
            cur = cur[list_index]
            continue
        if is_last:
            cur.setdefault(part, value)
            return
        if part not in cur or cur[part] in ({}, None, ""):
            cur[part] = {} if next_part and not next_part.isdigit() else []
        cur = cur[part]


def replace_or_insert_question(component: dict, question: dict, after_variable: str | None = None) -> None:
    for idx, existing in enumerate(component["questions"]):
        if existing["variable"] == question["variable"]:
            component["questions"][idx] = question
            return
    insert_at = len(component["questions"])
    if after_variable:
        for idx, existing in enumerate(component["questions"]):
            if existing["variable"] == after_variable:
                insert_at = idx + 1
                break
    component["questions"].insert(insert_at, question)


SCRIPT_DIR = pathlib.Path(__file__).resolve().parent
ROOT = SCRIPT_DIR.parent
INGRESS_CLASS_ENV_VARS = ("CCF_INGRESS_CLASS", "INGRESS_CLASS")
INGRESS_KUBECONFIG_ENV_VARS = ("CCF_INGRESS_KUBECONFIG", "VALIDATION_KUBECONFIG_PATH", "KUBECONFIG")
KNOWN_CCF_INGRESS_CLASS = "taikun"


def iter_kubeconfig_candidates() -> list[pathlib.Path]:
    candidates = []
    seen = set()
    for env_var in INGRESS_KUBECONFIG_ENV_VARS:
        raw_value = os.environ.get(env_var, "").strip()
        if not raw_value:
            continue
        path = pathlib.Path(raw_value).expanduser()
        key = str(path.resolve()) if path.exists() else str(path)
        if key in seen:
            continue
        seen.add(key)
        candidates.append(path)
    reports_dir = ROOT / "reports"
    if reports_dir.exists():
        for pattern in ("*kubeconfig*.yaml", "*kubeconfig*.yml"):
            for path in sorted(reports_dir.glob(pattern)):
                key = str(path.resolve())
                if key in seen:
                    continue
                seen.add(key)
                candidates.append(path)
    return candidates


def detect_ingress_class_default() -> str:
    for env_var in INGRESS_CLASS_ENV_VARS:
        ingress_class = os.environ.get(env_var, "").strip()
        if ingress_class:
            return ingress_class

    for kubeconfig in iter_kubeconfig_candidates():
        if not kubeconfig.exists():
            continue
        try:
            result = subprocess.run(
                ["kubectl", "--kubeconfig", str(kubeconfig), "get", "ingressclass", "-o", "json"],
                text=True,
                capture_output=True,
                check=False,
                timeout=5,
            )
        except FileNotFoundError:
            return ""
        except subprocess.TimeoutExpired:
            continue
        if result.returncode != 0:
            continue
        try:
            payload = json.loads(result.stdout or "{}")
        except json.JSONDecodeError:
            continue
        items = payload.get("items", [])
        default_classes = []
        discovered_classes = []
        for item in items:
            metadata = item.get("metadata", {})
            name = metadata.get("name", "").strip()
            if not name:
                continue
            discovered_classes.append(name)
            annotations = metadata.get("annotations", {})
            if annotations.get("ingressclass.kubernetes.io/is-default-class", "").lower() == "true":
                default_classes.append(name)
        if default_classes:
            return default_classes[0]
        if len(discovered_classes) == 1:
            return discovered_classes[0]
        try:
            ingress_result = subprocess.run(
                ["kubectl", "--kubeconfig", str(kubeconfig), "get", "ingress", "-A", "-o", "json"],
                text=True,
                capture_output=True,
                check=False,
                timeout=5,
            )
        except subprocess.TimeoutExpired:
            continue
        if ingress_result.returncode != 0:
            continue
        try:
            ingress_payload = json.loads(ingress_result.stdout or "{}")
        except json.JSONDecodeError:
            continue
        ingress_classes = []
        for item in ingress_payload.get("items", []):
            spec = item.get("spec", {})
            ingress_class = spec.get("ingressClassName", "").strip()
            if not ingress_class:
                ingress_class = item.get("metadata", {}).get("annotations", {}).get("kubernetes.io/ingress.class", "").strip()
            if ingress_class and ingress_class not in ingress_classes:
                ingress_classes.append(ingress_class)
        if len(ingress_classes) == 1:
            return ingress_classes[0]
    return KNOWN_CCF_INGRESS_CLASS


SERVICE_TYPE_OPTIONS = ["ClusterIP", "LoadBalancer", "NodePort"]
DEFAULT_CHART_VERSION = "0.1.0"
STATE_PATH = pathlib.Path(__file__).with_name("catalog_state.json")
CHART_MEDIA = {
    "cert-manager": {
        "icon": "https://raw.githubusercontent.com/cert-manager/community/4d35a69437d21b76322157e6284be4cd64e6d2b7/logo/logo-small.png",
        "home": "https://cert-manager.io",
    },
    "external-dns": {
        "icon": "https://github.com/kubernetes-sigs/external-dns/raw/master/docs/img/external-dns.png",
        "home": "https://github.com/kubernetes-sigs/external-dns/",
    },
    "istio": {
        "icon": "https://istio.io/latest/favicons/android-192x192.png",
        "home": "https://istio.io",
    },
    "harbor": {
        "icon": "https://raw.githubusercontent.com/goharbor/website/main/static/img/logos/harbor-icon-color.png",
        "home": "https://goharbor.io",
    },
    "cloudnative-pg": {
        "icon": "https://raw.githubusercontent.com/cloudnative-pg/artwork/main/cloudnativepg-logo.svg",
        "home": "https://cloudnative-pg.io",
    },
    "eck-operator": {
        "icon": "https://helm.elastic.co/icons/eck.png",
        "home": "https://github.com/elastic/cloud-on-k8s",
    },
    "eck-stack": {
        "icon": "https://helm.elastic.co/icons/eck.png",
        "home": "https://github.com/elastic/cloud-on-k8s",
    },
    "grafana": {
        "icon": "https://artifacthub.io/image/b4fed1a7-6c8f-4945-b99d-096efa3e4116",
        "home": "https://grafana.com",
    },
    "jupyterhub": {
        "icon": "https://hub.jupyter.org/helm-chart/images/hublogo.svg",
        "home": "https://z2jh.jupyter.org",
    },
    "ollama": {
        "icon": "https://ollama.ai/public/ollama.png",
        "home": "https://ollama.ai/",
    },
    "backstage": {
        "icon": "https://raw.githubusercontent.com/cncf/artwork/master/projects/backstage/icon/color/backstage-icon-color.svg",
        "home": "https://backstage.io",
    },
    "trino": {
        "icon": "https://trino.io/assets/trino.png",
        "home": "https://trino.io/",
    },
    "clickhouse-operator": {
        "icon": "https://clickhouse.com/docs/img/clickhouse-operator-logo.svg",
        "home": "https://github.com/ClickHouse/clickhouse-operator",
    },
    "valkey": {
        "icon": "https://dyltqmyl993wv.cloudfront.net/assets/stacks/valkey/img/valkey-stack-220x234.png",
        "home": "https://valkey.io/valkey-helm/",
    },
    "openmetadata": {
        "icon": "https://open-metadata.org/assets/favicon.png",
        "home": "https://open-metadata.org/",
    },
    "netbox": {
        "icon": "https://raw.githubusercontent.com/netbox-community/netbox/main/docs/netbox_logo_light.svg",
        "home": "https://netbox.dev/",
    },
    "chaos-mesh": {
        "icon": "https://raw.githubusercontent.com/chaos-mesh/chaos-mesh/master/static/logo.svg",
        "home": "https://chaos-mesh.org",
    },
}


CURATED_COMPONENTS = [
    {
        "id": "cert-manager",
        "display_name": "cert-manager",
        "package_name": "ccf-cert-manager",
        "namespace": "cert-manager",
        "source_classification": "official",
        "packaging_mode": "curated-wrapper",
        "questions_support": True,
        "smoke_profile": "default",
        "image_source_choice": "upstream-official",
        "notes": "Official Jetstack chart with lightweight monitoring defaults for CCF projects.",
        "dependencies": [
            {
                "name": "cert-manager",
                "repository": "https://charts.jetstack.io",
                "version": "v1.20.2",
                "app_version": "v1.20.2",
            }
        ],
        "values": {
            "cert-manager": {
                "installCRDs": True,
                "prometheus": {"enabled": False},
                "replicaCount": 1,
                "cainjector": {"replicaCount": 1},
                "webhook": {
                    "replicaCount": 1,
                    "timeoutSeconds": 30,
                    "serviceType": "ClusterIP",
                },
            }
        },
        "questions": [
            q(
                "cert-manager.installCRDs",
                "Install CRDs",
                "boolean",
                True,
                "Install cert-manager CRDs as part of the chart.",
                "Operator",
            ),
            q(
                "cert-manager.prometheus.enabled",
                "Enable Prometheus metrics",
                "boolean",
                False,
                "Expose cert-manager metrics service resources.",
                "Observability",
            ),
            q(
                "cert-manager.webhook.timeoutSeconds",
                "Webhook timeout",
                "int",
                30,
                "Admission webhook timeout in seconds.",
                "Operator",
                required=True,
            ),
            q(
                "cert-manager.webhook.serviceType",
                "Webhook service type",
                "enum",
                "ClusterIP",
                "Service exposure mode for the webhook service.",
                "Networking",
                options=SERVICE_TYPE_OPTIONS,
            ),
        ],
    },
    {
        "id": "external-dns",
        "display_name": "external-dns",
        "package_name": "ccf-external-dns",
        "namespace": "external-dns",
        "source_classification": "official",
        "packaging_mode": "curated-wrapper",
        "questions_support": True,
        "smoke_profile": "needs-overrides",
        "image_source_choice": "upstream-official",
        "notes": (
            "Official Kubernetes SIGs chart. Live validation usually needs provider-specific "
            "credentials and domain filters."
        ),
        "dependencies": [
            {
                "name": "external-dns",
                "repository": "https://kubernetes-sigs.github.io/external-dns/",
                "version": "1.20.0",
                "app_version": "0.20.0",
            }
        ],
        "values": {
            "external-dns": {
                "provider": {"name": "aws"},
                "serviceAccount": {"create": True},
                "txtOwnerId": "ccf-external-dns",
                "sources": ["service", "ingress"],
                "domainFilters": [],
                "policy": "upsert-only",
                "registry": "txt",
                "interval": "1m",
                "triggerLoopOnEvent": False,
            }
        },
        "questions": [
            q(
                "external-dns.provider.name",
                "DNS provider",
                "string",
                "aws",
                "Provider name accepted by the upstream external-dns chart.",
                "Provider",
                required=True,
            ),
            q(
                "external-dns.txtOwnerId",
                "TXT owner ID",
                "string",
                "ccf-external-dns",
                "Identifier used for TXT registry ownership records.",
                "Provider",
                required=True,
            ),
            q(
                "external-dns.sources",
                "Watched sources",
                "listofstrings",
                ["service", "ingress"],
                "Resource sources external-dns should watch.",
                "Application",
            ),
            q(
                "external-dns.domainFilters",
                "Domain filters",
                "listofstrings",
                [],
                "Optional list of DNS zones to scope the controller to.",
                "Provider",
            ),
            q(
                "external-dns.policy",
                "Update policy",
                "enum",
                "upsert-only",
                "How external-dns should apply record changes.",
                "Provider",
                options=["upsert-only", "sync", "create-only"],
            ),
        ],
    },
    {
        "id": "istio",
        "display_name": "Istio",
        "package_name": "ccf-istio",
        "namespace": "istio-system",
        "source_classification": "official",
        "packaging_mode": "curated-wrapper",
        "questions_support": True,
        "smoke_profile": "default",
        "image_source_choice": "upstream-official",
        "notes": "Official Istio control-plane wrapper combining the base and istiod charts.",
        "dependencies": [
            {
                "name": "base",
                "repository": "https://istio-release.storage.googleapis.com/charts",
                "version": "1.29.2",
                "app_version": "1.29.2",
            },
            {
                "name": "istiod",
                "repository": "https://istio-release.storage.googleapis.com/charts",
                "version": "1.29.2",
                "app_version": "1.29.2",
            },
        ],
        "values": {
            "base": {
                "global": {
                    "istioNamespace": "istio-system",
                    "resourceScope": "namespace",
                },
                "defaultRevision": "default",
            },
            "istiod": {
                "global": {"istioNamespace": "istio-system"},
                "revision": "default",
                "replicaCount": 1,
                "meshConfig": {"accessLogFile": "/dev/stdout"},
                "resources": {
                    "requests": {"cpu": "250m", "memory": "512Mi"},
                },
            },
        },
        "questions": [
            q(
                "base.global.istioNamespace",
                "Istio namespace",
                "string",
                "istio-system",
                "Namespace used for Istio control-plane resources.",
                "Operator",
                required=True,
            ),
            q(
                "base.defaultRevision",
                "Default revision",
                "string",
                "default",
                "Revision label installed by the Istio base chart.",
                "Operator",
                required=True,
            ),
            q(
                "base.global.resourceScope",
                "Resource scope",
                "enum",
                "namespace",
                "Resource ownership scope for the Istio base chart.",
                "Operator",
                options=["all", "cluster", "namespace"],
            ),
            q(
                "istiod.replicaCount",
                "istiod replicas",
                "int",
                1,
                "Number of istiod replicas to run.",
                "Operator",
                required=True,
            ),
            q(
                "istiod.meshConfig.accessLogFile",
                "Access log file",
                "string",
                "/dev/stdout",
                "Mesh access log target used by the control plane.",
                "Observability",
            ),
        ],
    },
    {
        "id": "harbor",
        "display_name": "Harbor",
        "package_name": "ccf-harbor",
        "namespace": "harbor",
        "source_classification": "official",
        "packaging_mode": "curated-wrapper",
        "questions_support": True,
        "smoke_profile": "needs-overrides",
        "image_source_choice": "upstream-official",
        "notes": (
            "Official Harbor chart. Initial defaults keep upstream images because Harbor "
            "ships multiple tightly coupled components."
        ),
        "dependencies": [
            {
                "name": "harbor",
                "repository": "https://helm.goharbor.io",
                "version": "1.18.3",
                "app_version": "2.14.3",
            }
        ],
        "values": {
            "harbor": {
                "expose": {
                    "type": "ingress",
                    "tls": {"enabled": False, "certSource": "none"},
                    "ingress": {"className": "", "hosts": {"core": "harbor.local"}},
                },
                "externalURL": "http://harbor.local",
                "persistence": {
                    "enabled": True,
                    "persistentVolumeClaim": {
                        "registry": {"storageClass": "", "size": "5Gi"},
                        "database": {"storageClass": "", "size": "1Gi"},
                        "redis": {"storageClass": "", "size": "1Gi"},
                        "trivy": {"storageClass": "", "size": "5Gi"},
                    },
                },
            }
        },
        "questions": [
            q(
                "harbor.expose.ingress.className",
                "Ingress class",
                "string",
                "",
                "Ingress class used when exposing Harbor through CCF-managed ingress.",
                "Networking",
            ),
            q(
                "harbor.expose.ingress.hosts.core",
                "Core hostname",
                "string",
                "harbor.local",
                "Primary hostname for the Harbor UI and API.",
                "Networking",
                required=True,
            ),
            q(
                "harbor.externalURL",
                "External URL",
                "string",
                "http://harbor.local",
                "Public URL CCF operators use to access Harbor.",
                "Networking",
                required=True,
            ),
            q(
                "harbor.persistence.persistentVolumeClaim.registry.storageClass",
                "Registry storage class",
                "string",
                "",
                "StorageClass for Harbor registry data.",
                "Storage",
            ),
            q(
                "harbor.persistence.persistentVolumeClaim.registry.size",
                "Registry PVC size",
                "string",
                "5Gi",
                "PVC size for the Harbor registry component.",
                "Storage",
                required=True,
            ),
        ],
    },
    {
        "id": "cloudnative-pg",
        "display_name": "CloudNativePG",
        "package_name": "ccf-cloudnative-pg",
        "namespace": "cnpg-system",
        "source_classification": "official",
        "packaging_mode": "curated-wrapper",
        "questions_support": True,
        "smoke_profile": "default",
        "image_source_choice": "upstream-official",
        "notes": "Namespace-scoped operator defaults are used for safer CCF project installs.",
        "dependencies": [
            {
                "name": "cloudnative-pg",
                "repository": "https://cloudnative-pg.github.io/charts",
                "version": "0.28.0",
                "app_version": "1.29.0",
            }
        ],
        "values": {
            "cloudnative-pg": {
                "config": {"clusterWide": False},
                "service": {"type": "ClusterIP"},
                "monitoring": {"podMonitorEnabled": False},
                "image": {
                    "repository": "ghcr.io/cloudnative-pg/cloudnative-pg",
                    "tag": "1.29.0",
                },
            }
        },
        "questions": [
            q(
                "cloudnative-pg.config.clusterWide",
                "Cluster-wide operator",
                "boolean",
                False,
                "Enable cluster-wide operator scope. Keep disabled for per-project CCF deployments.",
                "Operator",
            ),
            q(
                "cloudnative-pg.service.type",
                "Webhook service type",
                "enum",
                "ClusterIP",
                "Kubernetes service type for the operator webhook.",
                "Networking",
                options=SERVICE_TYPE_OPTIONS,
            ),
            q(
                "cloudnative-pg.monitoring.podMonitorEnabled",
                "Enable PodMonitor",
                "boolean",
                False,
                "Turn on PodMonitor resources when Prometheus Operator is available in the project.",
                "Observability",
            ),
            q(
                "cloudnative-pg.image.repository",
                "Operator image repository",
                "string",
                "ghcr.io/cloudnative-pg/cloudnative-pg",
                "Container image repository for the CloudNativePG operator.",
                "Images",
                required=True,
            ),
        ],
    },
    {
        "id": "eck-operator",
        "display_name": "Elastic ECK Operator",
        "package_name": "ccf-eck-operator",
        "namespace": "elastic-system",
        "source_classification": "official",
        "packaging_mode": "curated-wrapper",
        "questions_support": True,
        "smoke_profile": "default",
        "image_source_choice": "upstream-official",
        "notes": "Elastic's operator is packaged separately so the stack chart can be validated after it.",
        "dependencies": [
            {
                "name": "eck-operator",
                "repository": "https://helm.elastic.co",
                "version": "3.3.2",
                "app_version": "3.3.2",
            }
        ],
        "values": {
            "eck-operator": {
                "createClusterScopedResources": False,
                "managedNamespaces": [],
                "installCRDs": True,
                "config": {"validateStorageClass": False},
                "webhook": {"enabled": False},
                "resources": {"requests": {"cpu": "100m", "memory": "150Mi"}},
            }
        },
        "questions": [
            q(
                "eck-operator.createClusterScopedResources",
                "Create cluster-scoped resources",
                "boolean",
                False,
                "Keep disabled to reduce blast radius in shared CCF projects.",
                "Operator",
            ),
            q(
                "eck-operator.installCRDs",
                "Install CRDs",
                "boolean",
                True,
                "Install the Elastic CRDs required by stack resources.",
                "Operator",
            ),
            q(
                "eck-operator.webhook.enabled",
                "Enable webhook",
                "boolean",
                False,
                "Keep disabled for namespace-scoped validation profiles.",
                "Operator",
            ),
            q(
                "eck-operator.config.validateStorageClass",
                "Validate storage classes",
                "boolean",
                False,
                "Keep disabled when cluster-scoped resources are turned off.",
                "Operator",
            ),
            q(
                "eck-operator.resources.requests.cpu",
                "CPU request",
                "string",
                "100m",
                "CPU request for the ECK operator deployment.",
                "Resources",
                required=True,
            ),
            q(
                "eck-operator.resources.requests.memory",
                "Memory request",
                "string",
                "150Mi",
                "Memory request for the ECK operator deployment.",
                "Resources",
                required=True,
            ),
        ],
    },
    {
        "id": "eck-stack",
        "display_name": "Elastic ECK Stack",
        "package_name": "ccf-eck-stack",
        "namespace": "elastic-stack",
        "source_classification": "official",
        "packaging_mode": "curated-wrapper",
        "questions_support": True,
        "smoke_profile": "needs-overrides",
        "image_source_choice": "upstream-official",
        "notes": (
            "Validated only after the ECK operator is installed. The default profile keeps the "
            "stack small and enables Elasticsearch plus Kibana."
        ),
        "dependencies": [
            {
                "name": "eck-stack",
                "repository": "https://helm.elastic.co",
                "version": "0.18.2",
                "app_version": "",
            }
        ],
        "values": {
            "eck-stack": {
                "eck-elasticsearch": {"enabled": True},
                "eck-kibana": {"enabled": True},
                "eck-agent": {"enabled": False},
            }
        },
        "questions": [
            q(
                "eck-stack.eck-elasticsearch.enabled",
                "Enable Elasticsearch",
                "boolean",
                True,
                "Install the Elasticsearch example resources managed by ECK.",
                "Stack",
            ),
            q(
                "eck-stack.eck-kibana.enabled",
                "Enable Kibana",
                "boolean",
                True,
                "Install the Kibana example resources managed by ECK.",
                "Stack",
            ),
            q(
                "eck-stack.eck-agent.enabled",
                "Enable Elastic Agent",
                "boolean",
                False,
                "Enable Agent resources only when additional Fleet settings are supplied.",
                "Stack",
            ),
        ],
    },
    {
        "id": "grafana",
        "display_name": "Grafana",
        "package_name": "ccf-grafana",
        "namespace": "grafana",
        "source_classification": "official",
        "packaging_mode": "curated-wrapper",
        "questions_support": True,
        "smoke_profile": "default",
        "image_source_choice": "upstream-official",
        "notes": "Initial defaults remain close to upstream and keep ingress off by default.",
        "dependencies": [
            {
                "name": "grafana",
                "repository": "https://grafana.github.io/helm-charts",
                "version": "10.5.15",
                "app_version": "12.3.1",
            }
        ],
        "values": {
            "grafana": {
                "service": {"type": "ClusterIP"},
                "ingress": {"enabled": False},
                "persistence": {"enabled": True, "size": "10Gi"},
                "admin": {"existingSecret": ""},
            }
        },
        "questions": [
            q(
                "grafana.service.type",
                "Service type",
                "enum",
                "ClusterIP",
                "Service exposure mode for Grafana.",
                "Networking",
                options=SERVICE_TYPE_OPTIONS,
            ),
            q(
                "grafana.ingress.enabled",
                "Enable ingress",
                "boolean",
                False,
                "Create an ingress for Grafana.",
                "Networking",
            ),
            q(
                "grafana.persistence.enabled",
                "Enable persistence",
                "boolean",
                True,
                "Persist dashboards and plugins across restarts.",
                "Storage",
            ),
            q(
                "grafana.persistence.size",
                "Grafana PVC size",
                "string",
                "10Gi",
                "Persistent volume size for Grafana data.",
                "Storage",
                required=True,
            ),
        ],
    },
    {
        "id": "jupyterhub",
        "display_name": "JupyterHub",
        "package_name": "ccf-jupyterhub",
        "namespace": "jupyterhub",
        "source_classification": "official",
        "packaging_mode": "curated-wrapper",
        "questions_support": True,
        "smoke_profile": "needs-overrides",
        "image_source_choice": "upstream-official",
        "notes": "Proxy service is normalized to ClusterIP to fit most CCF projects.",
        "dependencies": [
            {
                "name": "jupyterhub",
                "repository": "https://hub.jupyter.org/helm-chart/",
                "version": "4.3.3",
                "app_version": "5.4.4",
            }
        ],
        "values": {
            "jupyterhub": {
                "proxy": {"service": {"type": "ClusterIP"}},
                "ingress": {"enabled": False},
                "singleuser": {"storage": {"capacity": "10Gi"}},
                "hub": {"config": {"JupyterHub": {"admin_access": True}}},
            }
        },
        "questions": [
            q(
                "jupyterhub.proxy.service.type",
                "Proxy service type",
                "enum",
                "ClusterIP",
                "Service type for the proxy-public service.",
                "Networking",
                options=SERVICE_TYPE_OPTIONS,
            ),
            q(
                "jupyterhub.ingress.enabled",
                "Enable ingress",
                "boolean",
                False,
                "Create an ingress in front of JupyterHub.",
                "Networking",
            ),
            q(
                "jupyterhub.singleuser.storage.capacity",
                "Singleuser storage size",
                "string",
                "10Gi",
                "Storage allocation for each notebook user.",
                "Storage",
                required=True,
            ),
            q(
                "jupyterhub.hub.config.JupyterHub.admin_access",
                "Enable admin access",
                "boolean",
                True,
                "Allow administrators to access user servers for support.",
                "Application",
            ),
        ],
    },
    {
        "id": "ollama",
        "display_name": "Ollama",
        "package_name": "ccf-ollama",
        "namespace": "ollama",
        "source_classification": "community",
        "packaging_mode": "curated-wrapper",
        "questions_support": True,
        "smoke_profile": "needs-overrides",
        "image_source_choice": "upstream-official",
        "notes": "Community chart. Default profile keeps networking internal and persistence enabled.",
        "dependencies": [
            {
                "name": "ollama",
                "repository": "https://helm.otwld.com/",
                "version": "1.54.0",
                "app_version": "0.19.0",
            }
        ],
        "values": {
            "ollama": {
                "service": {"type": "ClusterIP"},
                "ingress": {
                    "enabled": False,
                    "className": "",
                    "hosts": [{"host": "ollama.local", "paths": [{"path": "/", "pathType": "Prefix"}]}],
                    "tls": [],
                },
                "persistentVolume": {"enabled": True, "size": "30Gi"},
                "ollama": {"models": {"pull": []}},
            }
        },
        "questions": [
            q(
                "ollama.service.type",
                "Service type",
                "enum",
                "ClusterIP",
                "Service exposure mode for the Ollama API.",
                "Networking",
                options=SERVICE_TYPE_OPTIONS,
            ),
            q(
                "ollama.ingress.enabled",
                "Enable ingress",
                "boolean",
                False,
                "Expose Ollama through ingress.",
                "Networking",
            ),
            q(
                "ollama.persistentVolume.size",
                "Model PVC size",
                "string",
                "30Gi",
                "Persistent storage size for downloaded models.",
                "Storage",
                required=True,
            ),
            q(
                "ollama.ingress.hosts[0].host",
                "Ingress hostname",
                "string",
                "ollama.local",
                "Primary hostname used when ingress is enabled.",
                "Networking",
            ),
        ],
    },
    {
        "id": "backstage",
        "display_name": "Backstage",
        "package_name": "ccf-backstage",
        "namespace": "backstage",
        "source_classification": "official",
        "packaging_mode": "curated-wrapper",
        "questions_support": True,
        "smoke_profile": "manual-only",
        "image_source_choice": "upstream-official",
        "notes": (
            "The official chart currently depends on Bitnami common/postgresql artifacts. "
            "This wrapper keeps postgresql disabled by default and marks validation manual-only."
        ),
        "dependencies": [
            {
                "name": "backstage",
                "repository": "https://backstage.github.io/charts",
                "version": "2.6.3",
                "app_version": "",
            }
        ],
        "values": {
            "backstage": {
                "ingress": {"enabled": False, "className": "", "host": ""},
                "service": {"type": "ClusterIP"},
                "backstage": {"replicas": 1},
                "postgresql": {"enabled": False},
            }
        },
        "questions": [
            q(
                "backstage.ingress.enabled",
                "Enable ingress",
                "boolean",
                False,
                "Expose Backstage through an ingress resource.",
                "Networking",
            ),
            q(
                "backstage.ingress.host",
                "Ingress hostname",
                "string",
                "",
                "Hostname used when ingress is enabled.",
                "Networking",
            ),
            q(
                "backstage.service.type",
                "Service type",
                "enum",
                "ClusterIP",
                "Service exposure mode for the Backstage backend.",
                "Networking",
                options=SERVICE_TYPE_OPTIONS,
            ),
            q(
                "backstage.backstage.replicas",
                "Replica count",
                "int",
                1,
                "Number of Backstage application replicas.",
                "Application",
                required=True,
            ),
        ],
    },
    {
        "id": "trino",
        "display_name": "Trino",
        "package_name": "ccf-trino",
        "namespace": "trino",
        "source_classification": "official",
        "packaging_mode": "curated-wrapper",
        "questions_support": True,
        "smoke_profile": "default",
        "image_source_choice": "upstream-official",
        "notes": "Internal-only service defaults keep Trino easy to validate inside a project.",
        "dependencies": [
            {
                "name": "trino",
                "repository": "https://trinodb.github.io/charts/",
                "version": "1.42.1",
                "app_version": "479",
            }
        ],
        "values": {
            "trino": {
                "service": {"type": "ClusterIP"},
                "ingress": {"enabled": False, "className": "", "hosts": [], "tls": []},
                "server": {"workers": 2},
                "coordinator": {"jvm": {"maxHeapSize": "2G"}},
                "worker": {"jvm": {"maxHeapSize": "2G"}},
            }
        },
        "questions": [
            q(
                "trino.service.type",
                "Service type",
                "enum",
                "ClusterIP",
                "Service exposure mode for the Trino coordinator.",
                "Networking",
                options=SERVICE_TYPE_OPTIONS,
            ),
            q(
                "trino.ingress.enabled",
                "Enable ingress",
                "boolean",
                False,
                "Expose Trino through an ingress resource.",
                "Networking",
            ),
            q(
                "trino.server.workers",
                "Worker count",
                "int",
                2,
                "Number of Trino worker pods.",
                "Application",
                required=True,
            ),
            q(
                "trino.coordinator.jvm.maxHeapSize",
                "Coordinator JVM heap",
                "string",
                "2G",
                "Heap size for the Trino coordinator JVM.",
                "Resources",
                required=True,
            ),
        ],
    },
    {
        "id": "clickhouse-operator",
        "display_name": "ClickHouse Operator",
        "package_name": "ccf-clickhouse-operator",
        "namespace": "clickhouse-operator",
        "source_classification": "official",
        "packaging_mode": "curated-wrapper",
        "questions_support": True,
        "smoke_profile": "default",
        "image_source_choice": "upstream-official",
        "notes": "Official ClickHouse operator chart from GHCR OCI.",
        "dependencies": [
            {
                "name": "clickhouse-operator-helm",
                "repository": "oci://ghcr.io/clickhouse",
                "version": "0.0.3",
                "app_version": "v0.0.3",
            }
        ],
        "values": {
            "clickhouse-operator-helm": {
                "manager": {
                    "replicas": 1,
                    "resources": {
                        "requests": {"cpu": "10m", "memory": "64Mi"},
                    },
                },
                "prometheus": {"service_monitor": False},
            }
        },
        "questions": [
            q(
                "clickhouse-operator-helm.manager.replicas",
                "Operator replicas",
                "int",
                1,
                "Number of ClickHouse operator replicas.",
                "Operator",
                required=True,
            ),
            q(
                "clickhouse-operator-helm.manager.resources.requests.cpu",
                "CPU request",
                "string",
                "10m",
                "CPU request for the ClickHouse operator manager.",
                "Resources",
                required=True,
            ),
            q(
                "clickhouse-operator-helm.manager.resources.requests.memory",
                "Memory request",
                "string",
                "64Mi",
                "Memory request for the ClickHouse operator manager.",
                "Resources",
                required=True,
            ),
            q(
                "clickhouse-operator-helm.prometheus.service_monitor",
                "Enable ServiceMonitor",
                "boolean",
                False,
                "Create ServiceMonitor resources when a Prometheus Operator is present.",
                "Observability",
            ),
        ],
    },
    {
        "id": "valkey",
        "display_name": "Valkey",
        "package_name": "ccf-valkey",
        "namespace": "valkey",
        "source_classification": "official",
        "packaging_mode": "curated-wrapper",
        "questions_support": True,
        "smoke_profile": "default",
        "image_source_choice": "upstream-official",
        "notes": "Official Valkey chart with conservative single-primary defaults.",
        "dependencies": [
            {
                "name": "valkey",
                "repository": "https://valkey.io/valkey-helm/",
                "version": "0.9.4",
                "app_version": "9.0.2",
            }
        ],
        "values": {
            "valkey": {
                "service": {"type": "ClusterIP"},
                "dataStorage": {"requestedSize": "8Gi"},
                "replica": {"enabled": False, "replicas": 2},
                "tls": {"enabled": False},
            }
        },
        "questions": [
            q(
                "valkey.service.type",
                "Service type",
                "enum",
                "ClusterIP",
                "Service exposure mode for Valkey.",
                "Networking",
                options=SERVICE_TYPE_OPTIONS,
            ),
            q(
                "valkey.dataStorage.requestedSize",
                "Primary PVC size",
                "string",
                "8Gi",
                "Persistent volume size for the primary Valkey node.",
                "Storage",
                required=True,
            ),
            q(
                "valkey.replica.enabled",
                "Enable replicas",
                "boolean",
                False,
                "Turn on replica nodes for read scaling and HA.",
                "Application",
            ),
            q(
                "valkey.tls.enabled",
                "Enable TLS",
                "boolean",
                False,
                "Enable TLS for Valkey client and replica traffic.",
                "Security",
            ),
        ],
    },
    {
        "id": "openmetadata",
        "display_name": "OpenMetadata",
        "package_name": "ccf-openmetadata",
        "namespace": "openmetadata",
        "source_classification": "official",
        "packaging_mode": "curated-wrapper",
        "questions_support": True,
        "smoke_profile": "manual-only",
        "image_source_choice": "upstream-official",
        "notes": (
            "The application chart expects external database and search services for a clean "
            "non-Bitnami setup. Validation remains manual-only until those overrides are supplied."
        ),
        "dependencies": [
            {
                "name": "openmetadata",
                "repository": "https://helm.open-metadata.org/",
                "version": "1.12.5",
                "app_version": "1.12.5",
            }
        ],
        "values": {
            "openmetadata": {
                "replicaCount": 1,
                "ingress": {"enabled": False, "className": ""},
                "openmetadata": {
                    "config": {
                        "database": {"host": "mysql"},
                        "elasticsearch": {"host": "opensearch"},
                        "pipelineServiceClientConfig": {
                            "enabled": False,
                            "k8s": {"namespace": ""},
                        },
                    }
                },
            }
        },
        "questions": [
            q(
                "openmetadata.ingress.enabled",
                "Enable ingress",
                "boolean",
                False,
                "Expose the OpenMetadata UI through ingress.",
                "Networking",
            ),
            q(
                "openmetadata.replicaCount",
                "Replica count",
                "int",
                1,
                "Number of OpenMetadata application replicas.",
                "Application",
                required=True,
            ),
            q(
                "openmetadata.openmetadata.config.pipelineServiceClientConfig.enabled",
                "Enable pipeline client",
                "boolean",
                False,
                "Enable the built-in pipeline client integration when an orchestration backend is available.",
                "Integrations",
            ),
            q(
                "openmetadata.openmetadata.config.pipelineServiceClientConfig.k8s.namespace",
                "Ingestion namespace",
                "string",
                "",
                "Namespace used for ingestion jobs when Kubernetes mode is enabled.",
                "Integrations",
            ),
        ],
    },
    {
        "id": "question-types-smoke",
        "display_name": "Question Types Smoke Test",
        "package_name": "ccf-question-types-smoke",
        "namespace": "question-types-smoke",
        "source_classification": "local",
        "packaging_mode": "standalone-test-chart",
        "questions_support": True,
        "smoke_profile": "default",
        "image_source_choice": "upstream-official",
        "notes": (
            "Standalone in-repo chart used to probe how CCF transports each Rancher-style "
            "questions.yaml type into Helm values. It keeps one prompt each for string, enum, "
            "boolean, int, and listofstrings while a values schema enforces their expected types. "
            "Validation manifests still only inject string and enum app parameters automatically, "
            "so the typed prompts can be exercised through the CCF MCP runner or manually through "
            "the CCF UI."
        ),
        "source_repository": "local://components/question-types-smoke",
        "app_version": "0.1.0",
        "dependencies": [],
        "values": {
            "questionTypesSmoke": {
                "stringValue": "alpha",
                "enumValue": "option-a",
                "booleanValue": True,
                "intValue": 7,
                "listValue": ["one", "two"],
                "image": {
                    "repository": "registry.k8s.io/pause",
                    "tag": "3.10",
                    "pullPolicy": "IfNotPresent",
                },
            }
        },
        "questions": [
            q(
                "questionTypesSmoke.stringValue",
                "String value",
                "string",
                "alpha",
                "String transport probe. This should arrive in Helm exactly as a string.",
                "Transport",
                required=True,
            ),
            q(
                "questionTypesSmoke.enumValue",
                "Enum value",
                "enum",
                "option-a",
                "Enum transport probe restricted by values.schema.json.",
                "Transport",
                options=["option-a", "option-b", "option-c"],
                required=True,
            ),
            q(
                "questionTypesSmoke.booleanValue",
                "Boolean value",
                "boolean",
                True,
                "Boolean transport probe. Schema validation should fail if CCF sends a string.",
                "Transport",
                required=True,
            ),
            q(
                "questionTypesSmoke.intValue",
                "Integer value",
                "int",
                7,
                "Integer transport probe. Schema validation should fail if CCF sends a quoted string.",
                "Transport",
                required=True,
            ),
            q(
                "questionTypesSmoke.listValue",
                "List of strings value",
                "listofstrings",
                ["one", "two"],
                "List transport probe. Schema validation should fail if CCF flattens the array.",
                "Transport",
                required=True,
            ),
        ],
    },
    {
        "id": "netbox",
        "display_name": "NetBox",
        "package_name": "ccf-netbox",
        "namespace": "netbox",
        "source_classification": "community",
        "packaging_mode": "curated-wrapper",
        "questions_support": True,
        "smoke_profile": "manual-only",
        "image_source_choice": "upstream-official",
        "notes": (
            "The community chart currently depends on Bitnami common/postgresql/valkey artifacts. "
            "Validation remains manual-only while external service wiring is supplied."
        ),
        "dependencies": [
            {
                "name": "netbox",
                "repository": "https://charts.netbox.oss.netboxlabs.com/",
                "version": "8.1.1",
                "app_version": "v4.5.8",
            }
        ],
        "values": {
            "netbox": {
                "service": {"type": "ClusterIP"},
                "ingress": {"enabled": False, "className": ""},
                "persistence": {
                    "enabled": True,
                    "storageClass": "",
                    "size": "5Gi",
                },
                "postgresql": {"enabled": False},
                "valkey": {"enabled": False},
            }
        },
        "questions": [
            q(
                "netbox.ingress.enabled",
                "Enable ingress",
                "boolean",
                False,
                "Expose NetBox through ingress.",
                "Networking",
            ),
            q(
                "netbox.ingress.className",
                "Ingress class",
                "string",
                "",
                "Ingress class used for the NetBox UI.",
                "Networking",
            ),
            q(
                "netbox.persistence.storageClass",
                "Storage class",
                "string",
                "",
                "StorageClass used for NetBox persistent data.",
                "Storage",
            ),
            q(
                "netbox.persistence.size",
                "PVC size",
                "string",
                "5Gi",
                "Persistent volume size for NetBox uploads and reports.",
                "Storage",
                required=True,
            ),
        ],
    },
    {
        "id": "chaos-mesh",
        "display_name": "Chaos Mesh",
        "package_name": "ccf-chaos-mesh",
        "namespace": "chaos-mesh",
        "source_classification": "official",
        "packaging_mode": "curated-wrapper",
        "questions_support": True,
        "smoke_profile": "needs-overrides",
        "image_source_choice": "upstream-official",
        "notes": "Dashboard is normalized to ClusterIP instead of the upstream NodePort default.",
        "dependencies": [
            {
                "name": "chaos-mesh",
                "repository": "https://charts.chaos-mesh.org",
                "version": "2.8.2",
                "app_version": "2.8.2",
            }
        ],
        "values": {
            "chaos-mesh": {
                "controllerManager": {"replicaCount": 1},
                "dashboard": {
                    "service": {"type": "ClusterIP"},
                    "ingress": {"enabled": False},
                    "persistentVolume": {"size": "5Gi"},
                },
            }
        },
        "questions": [
            q(
                "chaos-mesh.controllerManager.replicaCount",
                "Controller replicas",
                "int",
                1,
                "Number of controller-manager replicas to run.",
                "Operator",
                required=True,
            ),
            q(
                "chaos-mesh.dashboard.service.type",
                "Dashboard service type",
                "enum",
                "ClusterIP",
                "Service exposure mode for the Chaos Mesh dashboard.",
                "Networking",
                options=SERVICE_TYPE_OPTIONS,
            ),
            q(
                "chaos-mesh.dashboard.ingress.enabled",
                "Enable dashboard ingress",
                "boolean",
                False,
                "Create an ingress in front of the Chaos Mesh dashboard.",
                "Networking",
            ),
            q(
                "chaos-mesh.dashboard.persistentVolume.size",
                "Dashboard PVC size",
                "string",
                "5Gi",
                "Persistent volume size for dashboard workflow artifacts.",
                "Storage",
                required=True,
            ),
        ],
    },
]


EXCLUDED_COMPONENTS = [
    {
        "id": "rabbitmq",
        "reason": (
            "Not curated in this repository. Import an external community or vendor repository "
            "directly into CCF when RabbitMQ is needed."
        ),
    },
    {
        "id": "wordpress",
        "reason": (
            "Not curated in this repository. Import the upstream community repository directly "
            "into CCF if WordPress is needed."
        ),
    },
    {
        "id": "memcached",
        "reason": (
            "No maintained official or community Helm chart could be validated outside archived "
            "charts or Bitnami."
        ),
    },
]


INGRESS_CLASS_DEFAULT = detect_ingress_class_default()
INGRESS_CAPABILITIES = {
    "harbor": {
        "enable_path": None,
        "class_path": "harbor.expose.ingress.className",
        "host_path": "harbor.expose.ingress.hosts.core",
    },
    "grafana": {
        "enable_path": "grafana.ingress.enabled",
        "class_path": "grafana.ingress.className",
        "host_path": None,
    },
    "jupyterhub": {
        "enable_path": "jupyterhub.ingress.enabled",
        "class_path": "jupyterhub.ingress.ingressClassName",
        "host_path": None,
    },
    "ollama": {
        "enable_path": "ollama.ingress.enabled",
        "class_path": "ollama.ingress.className",
        "host_path": "ollama.ingress.hosts[0].host",
    },
    "backstage": {
        "enable_path": "backstage.ingress.enabled",
        "class_path": "backstage.ingress.className",
        "host_path": "backstage.ingress.host",
    },
    "trino": {
        "enable_path": "trino.ingress.enabled",
        "class_path": "trino.ingress.className",
        "host_path": None,
    },
    "openmetadata": {
        "enable_path": "openmetadata.ingress.enabled",
        "class_path": "openmetadata.ingress.className",
        "host_path": None,
    },
    "netbox": {
        "enable_path": "netbox.ingress.enabled",
        "class_path": "netbox.ingress.className",
        "host_path": None,
    },
    "chaos-mesh": {
        "enable_path": "chaos-mesh.dashboard.ingress.enabled",
        "class_path": "chaos-mesh.dashboard.ingress.className",
        "host_path": None,
    },
}


def ingress_class_question(component: dict, variable: str) -> dict:
    return q(
        variable,
        "Ingress class",
        "string",
        INGRESS_CLASS_DEFAULT,
        (
            f"Optional ingressClassName used when exposing {component['display_name']} through the "
            "cluster ingress controller. Leave blank to rely on the cluster default ingress class."
        ),
        "Networking",
    )


def apply_ingress_metadata() -> None:
    for component in CURATED_COMPONENTS:
        ingress = INGRESS_CAPABILITIES.get(component["id"])
        if not ingress:
            continue
        set_path_default(component["values"], ingress["class_path"], INGRESS_CLASS_DEFAULT)
        replace_or_insert_question(
            component,
            ingress_class_question(component, ingress["class_path"]),
            after_variable=ingress["enable_path"],
        )


def component_matrix():
    """Return a normalized list used by docs and validation scripts."""
    rows = []
    for item in CURATED_COMPONENTS:
        rows.append(
            {
                "requested_component": item["id"],
                "display_name": item["display_name"],
                "upstream_chart_source": component_source_repository(item),
                "packaged_chart_name": item["package_name"],
                "pinned_version": item["dependencies"][0]["version"] if item["dependencies"] else item.get("chart_version", DEFAULT_CHART_VERSION),
                "app_version": component_app_version(item),
                "default_namespace": item["namespace"],
                "source_classification": item["source_classification"],
                "packaging_mode": item["packaging_mode"],
                "questions_yaml_support": "yes" if item["questions_support"] else "no",
                "ccf_smoke_test_profile": item["smoke_profile"],
                "image_source_choice": item["image_source_choice"],
                "notes": item["notes"],
            }
        )
    for item in EXCLUDED_COMPONENTS:
        rows.append(
            {
                "requested_component": item["id"],
                "display_name": item["id"],
                "upstream_chart_source": "n/a",
                "packaged_chart_name": "excluded",
                "pinned_version": "n/a",
                "app_version": "n/a",
                "default_namespace": "n/a",
                "source_classification": "excluded",
                "packaging_mode": "excluded",
                "questions_yaml_support": "no",
                "ccf_smoke_test_profile": "manual-only",
                "image_source_choice": "n/a",
                "notes": item["reason"],
            }
        )
    return deepcopy(rows)


def load_catalog_state() -> dict:
    if not STATE_PATH.exists():
        return {}
    data = json.loads(STATE_PATH.read_text(encoding="utf-8"))
    return data if isinstance(data, dict) else {}


def apply_catalog_state() -> None:
    state = load_catalog_state()
    for component in CURATED_COMPONENTS:
        component_state = state.get(component["id"], {})
        component["chart_version"] = component_state.get("chart_version", DEFAULT_CHART_VERSION)
        dependency_state = component_state.get("dependencies", {})
        for dependency in component["dependencies"]:
            override = dependency_state.get(dependency["name"], {})
            for key in ("repository", "version", "app_version"):
                if key in override:
                    dependency[key] = override[key]


def apply_chart_media() -> None:
    for component in CURATED_COMPONENTS:
        component.update(CHART_MEDIA.get(component["id"], {}))


apply_chart_media()
apply_catalog_state()
apply_ingress_metadata()
