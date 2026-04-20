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

Standalone in-repo chart used to probe how CCF transports each Rancher-style questions.yaml type into Helm values. It keeps prompts for string, enum, boolean, and int, plus indexed string slots for list values because CCF currently does not preserve native list questions. Validation manifests now inject string, enum, boolean, and int app parameters automatically, while indexed list slots remain UI-only/manual overrides.

## Files

- `Chart.yaml`: chart metadata and any pinned upstream dependencies
- `values.yaml`: curated default values for CCF environments
- `questions.yaml`: catalog prompts exposed to operators
- `templates/NOTES.txt`: post-install guidance shown by Helm after install or upgrade

## References

- Source repository: `local://components/question-types-smoke`
- Project home: https://github.com/skotnicky/components
- Release notes: https://github.com/skotnicky/components/releases
