# ccf-question-types-smoke

Curated `Question Types Smoke Test` standalone chart for the Cloudera Cloud Factory components catalog.

## Purpose

This chart is maintained directly in this repository so CCF question transport can be tested against a small typed workload with a local `values.schema.json`.

## Upstream Dependencies

This chart has no external Helm dependencies.

## Defaults

- Namespace: `question-types-smoke`
- Smoke profile: `default`
- Image source choice: `upstream-official`
- Chart version: `0.1.0`
- App version: `0.1.0`

## Notes

Standalone in-repo chart used to probe how CCF transports each Rancher-style questions.yaml type into Helm values. It keeps one prompt each for string, enum, boolean, int, and listofstrings while a values schema enforces their expected types. Validation manifests still only inject string and enum app parameters automatically, so the typed prompts can be exercised through the CCF MCP runner or manually through the CCF UI.

## Files

- `Chart.yaml`: chart metadata and any pinned upstream dependencies
- `values.yaml`: curated default values for CCF environments
- `questions.yaml`: catalog prompts exposed to operators

## References

- Source repository: `local://components/question-types-smoke`
