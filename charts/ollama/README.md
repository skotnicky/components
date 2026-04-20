# ccf-ollama

Curated `Ollama` wrapper chart for the Cloudera Cloud Factory components catalog.

## Purpose

This chart packages upstream Helm dependencies with curated default values and a Rancher-style `questions.yaml` so it can be imported and installed more easily in CCF.

## Upstream Dependencies

- `ollama` from `https://helm.otwld.com/` at `1.54.0`

## Defaults

- Namespace: `ollama`
- Smoke profile: `needs-overrides`
- Image source choice: `upstream-official`
- Chart version: `0.1.2`
- App version: `0.19.0`

## Notes

Community chart. Default profile keeps networking internal and persistence enabled.

## Files

- `Chart.yaml`: chart metadata and any pinned upstream dependencies
- `values.yaml`: curated default values for CCF environments
- `questions.yaml`: catalog prompts exposed to operators

## References

- Source repository: `https://helm.otwld.com/`
- Project home: https://ollama.ai/
- Icon: https://ollama.ai/public/ollama.png
