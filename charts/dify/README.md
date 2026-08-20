# ccf-dify

Curated `Dify` wrapper chart for the Cloudera Cloud Factory components catalog.

## Purpose

This chart packages upstream Helm dependencies with curated default values and a Rancher-style `questions.yaml` so it can be imported and installed more easily in CCF.

## Upstream Dependencies

- `dify` from `https://borispolonsky.github.io/dify-helm` at `0.37.0`

## Defaults

- Namespace: `dify`
- Smoke profile: `manual-only`
- Image source choice: `upstream-official`
- Chart version: `0.1.0`
- App version: `1.14.2`

## Notes

Community BorisPolonsky Dify chart for building LLM applications. The curated profile keeps the bundled PostgreSQL, Redis, and Weaviate quickstart dependencies with single-instance sizing and internal-only networking. Validation stays manual-only until project-specific secret keys and, for production, external datastores are supplied.

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
