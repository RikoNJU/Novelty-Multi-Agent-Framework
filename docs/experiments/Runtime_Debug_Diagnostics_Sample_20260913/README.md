# Runtime Debug diagnostics fixed offline sample

This package is a deterministic, network-free acceptance fixture for the Runtime
Debug diagnostics integration. It was generated on the `lya` development baseline
recorded in `sample-fixed/manifest.json` with the following fixed facts:

- paper: `runtime-debug-sample`
- run: `sample-fixed`
- task: `NP-SAMPLE/T-SAMPLE`
- one failed Reader call for the non-existent `art_missing`
- one Gate A rejection for `CARD-SAMPLE`
- expected terminal status: `PARTIAL`

Review `sample-fixed/diagnostics/reader_failures.json` for the per-call diagnosis,
then compare its compact index with `sample-fixed/summary.json` and the readable
table in `sample-fixed/summary.md`. The package contains no paper text, quote,
model context, credentials, cookies, or API tokens.

Compatibility notes:

- Runtime terminal status now includes `PARTIAL`.
- `summary.json` adds `diagnostics` and optional `outcome` fields.
- `manifest.json` adds `runtime_diagnostics` with diagnostic schema versions.
- Runtime Debug disabled mode remains filesystem-side-effect free.
- `repair_artifact_line_endings.py` remains an explicit, default-dry-run
  maintenance command and is never imported or run by diagnostics.
