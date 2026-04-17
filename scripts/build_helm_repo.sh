#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
REPO_DIR="${REPO_DIR:-$ROOT_DIR/dist/helm-repo}"
HELM_REPO_URL="${HELM_REPO_URL:-}"
TMP_DIST_DIR="${TMP_DIST_DIR:-$ROOT_DIR/.tmp/helm-repo-packages}"
EXISTING_INDEX_PATH="$REPO_DIR/.existing-index.yaml"

if [[ -z "$HELM_REPO_URL" ]]; then
  echo "HELM_REPO_URL must be set to build a classic Helm repository index." >&2
  exit 1
fi

HELM_REPO_URL="${HELM_REPO_URL%/}"

rm -rf "$REPO_DIR"
rm -rf "$TMP_DIST_DIR"
mkdir -p "$REPO_DIR"
mkdir -p "$TMP_DIST_DIR"

python3 "$ROOT_DIR/scripts/seed_existing_helm_repo.py" \
  --repo-url "$HELM_REPO_URL" \
  --output-dir "$REPO_DIR" \
  --index-output "$EXISTING_INDEX_PATH"

DIST_DIR="$TMP_DIST_DIR" PUSH=0 bash "$ROOT_DIR/scripts/package_curated.sh" >/dev/null
cp "$TMP_DIST_DIR"/*.tgz "$REPO_DIR"/

if [[ -f "$EXISTING_INDEX_PATH" ]]; then
  helm repo index "$REPO_DIR" --url "$HELM_REPO_URL" --merge "$EXISTING_INDEX_PATH"
else
  helm repo index "$REPO_DIR" --url "$HELM_REPO_URL"
fi
rm -f "$EXISTING_INDEX_PATH"
rm -rf "$TMP_DIST_DIR"
touch "$REPO_DIR/.nojekyll"

cat > "$REPO_DIR/index.html" <<EOF
<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>CCF Helm Repository</title>
    <style>
      body {
        font-family: Arial, sans-serif;
        line-height: 1.5;
        margin: 2rem auto;
        max-width: 48rem;
        padding: 0 1rem;
      }
      code, pre {
        background: #f6f8fa;
        border-radius: 0.25rem;
      }
      code {
        padding: 0.125rem 0.25rem;
      }
      pre {
        overflow-x: auto;
        padding: 0.75rem 1rem;
      }
    </style>
  </head>
  <body>
    <main>
      <h1>CCF Helm Repository</h1>
      <p>
        This GitHub Pages site serves the curated Helm repository for Cloudera
        Cloud Factory.
      </p>
      <p>
        Use the base URL below with Helm or CCF. The repository index is
        available at <a href="index.yaml">index.yaml</a>.
      </p>
      <pre><code>helm repo add ccf ${HELM_REPO_URL}</code></pre>
      <pre><code>helm search repo ccf</code></pre>
    </main>
  </body>
</html>
EOF

echo "$REPO_DIR"
