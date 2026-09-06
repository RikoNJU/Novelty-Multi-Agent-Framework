# Runtime Debug Artifacts

Runtime debug recording is Harness-owned infrastructure and is enabled by
default. Each workflow run incrementally writes to:

```text
outputs/{paper_id}/runtime/{run_id}/
├── manifest.json
├── stages/
├── tools/
├── errors/
├── summary.json
└── summary.md
```

Terminal runs (`SUCCESS`, `FAILED`, and `INTERRUPTED`) also archive both summary
files under:

```text
docs/experiments/runtime/{paper_id}_{date}/{run_id}/
```

Each Tool Call records the arguments emitted by the model, the validated and
default-filled arguments used by the Harness, the full Tool observation, and
the normalized projection returned to the model. `failure_phase` distinguishes
`PRE_TOOL`, `TOOL_EXECUTION`, and `NORMALIZATION` failures. A successful empty
result remains `execution_status: SUCCESS` with `business_status: EMPTY`.

## Configuration

The project settings file accepts:

```json
{
  "runtime_debug": {
    "enabled": true,
    "output_root": "outputs",
    "archive_root": "docs/experiments/runtime",
    "max_inline_bytes": 256000
  }
}
```

Set `enabled` to `false` to disable all runtime-debug filesystem writes. This
does not change prompts, Tool definitions, Tool arguments, workflow routing, or
business results.

Values under keys matching `api_key`, `token`, `secret`, `password`,
`authorization`, or `cookie` are recursively replaced with
`***REDACTED***`. Large strings and byte sequences are represented by size and
SHA-256 metadata rather than duplicated inline. Existing `Path` values are
represented as artifact references containing path, size, and SHA-256 when the
target is a file.
