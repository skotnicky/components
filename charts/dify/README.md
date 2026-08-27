# ccf-dify

Curated `Dify` wrapper chart for the Cloudera Cloud Factory components catalog.

## Purpose

This chart packages upstream Helm dependencies with curated default values and a Rancher-style `questions.yaml` so it can be imported and installed more easily in CCF.

## Upstream Dependencies

- `dify` from `https://borispolonsky.github.io/dify-helm` at `0.37.0`

## Defaults

- Namespace: `dify`
- Smoke profile: `needs-overrides`
- Image source choice: `upstream-official`
- Chart version: `0.1.2`
- App version: `1.14.2`

## Notes

Community BorisPolonsky Dify chart for building LLM applications. The upstream Bitnami PostgreSQL and Redis subcharts are disabled to keep the catalog free of Bitnami charts; instead the wrapper bundles non-Bitnami PostgreSQL (official postgres image) and Valkey (official valkey image) that publish the postgres-rw and valkey Services the Dify defaults target, so a fresh install is self-contained. Set bundledPostgres.enabled/bundledValkey.enabled to false to use external managed datastores instead. The non-Bitnami Weaviate vector store stays bundled from upstream, and a Helm hook fixes shared volume permissions so the API can write tenant keys under privkeys/ during first-time setup. Live validation typically needs storage-class overrides for the bundled data volumes.

## Files

- `Chart.yaml`: chart metadata and any pinned upstream dependencies
- `values.yaml`: curated default values for CCF environments
- `questions.yaml`: catalog prompts exposed to operators
- `templates/NOTES.txt`: post-install guidance shown by Helm after install or upgrade

## References

- Source repository: `https://borispolonsky.github.io/dify-helm`
- Project home: https://dify.ai/
- Release notes: https://github.com/langgenius/dify/releases
- Icon: https://avatars.githubusercontent.com/u/127165244
