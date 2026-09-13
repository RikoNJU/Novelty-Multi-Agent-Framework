# Runtime Debug Artifacts

Runtime debug recording is Harness-owned infrastructure and is enabled by
default. Each workflow run incrementally writes to:

```text
outputs/{paper_id}/runtime/{run_id}/
├── manifest.json
├── stages/
├── tools/
├── llm_calls/
├── errors/
├── diagnostics/
│   ├── reader.json
│   ├── reference_namespace.json
│   └── reviewer.json
├── summary.json
└── summary.md
```

Terminal runs (`SUCCESS`, `FAILED`, and `INTERRUPTED`) also archive both summary
files and diagnostics under:

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

## Standard entrypoints and run identity

The three standard entrypoints are truncation levels of one workflow, not three
independent business implementations:

| Entrypoint | Script | Role |
|---|---|---|
| Full Pipeline | `scripts/run_full_pipeline_experiment.py` | PDF/MinerU end-to-end acceptance |
| PaperInput Pipeline | `scripts/run_full_workflow_live.py` | primary experiment entrypoint, including Run A |
| Single Task | `scripts/run_single_research_task.py` | exact TaskResearcher + Gate A reproduction |

After Full Pipeline has produced `PaperInput`, it invokes the same
`NoveltyWorkflow(PaperInput)` used by PaperInput Pipeline. Its legacy `Recorder`
is retained only for pre-PaperInput timing and old experiment-report
compatibility; workflow stages, model/tool calls, and diagnostics use Runtime
Debug as their authoritative source. Do not add new workflow diagnostics to the
legacy Recorder.

Single Task requires `--paper-json`, `--point-id`, and `--task-id`. The point,
task, and corresponding SearchPlan must each match exactly; language is reported
from the selected task and is never used to select the first matching task.
Both `run_research_task` and Gate A (`validate_synthesis_input`) are finalized
before the run receives its terminal status.

Every manifest and summary records an `entrypoint` plus `input_identity`. The
latter contains the explicit PaperInput path and SHA-256, as well as point/task/
SearchPlan IDs when applicable. These fields are runtime metadata only and are
never copied into `PaperInput.metadata` or prompts.

## Current-run diagnostics

Runtime finalization runs the Reader failure, reference namespace, and Reviewer
inspectors against exactly the current `run_id`. Workspace manifests and
business artifacts remain the paper-level state those checks validate. Each CLI
also accepts `--run-id`; omitting it preserves its historical workspace view.

Diagnostic status uses `OK`, `WARNING`, `ERROR`, or `INCOMPLETE`. Missing early
business outputs and absent Reader calls are incomplete observations, not
business failures. Inspector exceptions are captured in their diagnostic JSON
and summary index and never change the workflow's terminal result. Diagnostics
are observational: they do not retry, repair, or mutate business state.

## Final Evidence Sufficiency Check

The `check_final_evidence_sufficiency` stage keeps its complete state input and
business output in the normal `input.json` and `output.json` files. Its
`meta.json` also contains a factual projection under:

```text
debug_details.final_evidence_sufficiency
```

The projection records:

- the effective `configured_cut`, current round, and `max_rounds`;
- the total number of final valid Cards presented to the check;
- each NoveltyPoint's `valid_card_count`, `required_card_count`, and deterministic
  `PASS` or `INSUFFICIENT` comparison;
- the structured `insufficient_final_evidence_points` emitted by the stage;
- whether the emitted list matches the count comparison;
- whether the current round limit permits the existing V0 supplement branch.

`summary.json` collects every round under
`final_evidence_sufficiency_checks`. Each entry also records the actually
executed next stage, such as `plan_supplement` or `synthesize_report`.
`summary.md` renders the same facts as a per-round table. These fields report
observed values and deterministic comparisons only; they do not evaluate
retrieval breadth, source diversity, evidence quality, or conclusion
credibility.
