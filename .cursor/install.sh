#!/usr/bin/env bash
# Idempotent Cloud Agent bootstrap for the Public CCF Helm OCI Catalog.
# Installs Helm, refreshes Python deps, regenerates curated charts, and
# pre-fetches upstream chart dependencies so validation runs offline afterwards.
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

HELM_VERSION="${HELM_VERSION:-v3.21.4}"

install_helm() {
  if command -v helm >/dev/null 2>&1; then
    echo "helm already installed: $(helm version --short 2>/dev/null || true)"
    return
  fi
  echo "Installing Helm ${HELM_VERSION}..."
  curl -fsSL https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3 \
    | DESIRED_VERSION="${HELM_VERSION}" bash
  helm version --short
}

install_helm

echo "Installing Python dependencies..."
python3 -m pip install --user --upgrade -r requirements.txt

echo "Regenerating curated charts and catalog matrix..."
python3 scripts/render_catalog.py

echo "Registering upstream Helm repositories..."
python3 scripts/ensure_helm_repos.py

echo "Building chart dependencies..."
for chart_dir in charts/*/; do
  if [[ -f "${chart_dir}Chart.yaml" ]]; then
    helm dependency build "${chart_dir}"
  fi
done

echo "Cloud Agent environment bootstrap complete."
