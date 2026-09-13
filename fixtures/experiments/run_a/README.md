# Run A frozen baseline

- Entrypoint: `scripts/run_full_workflow_live.py`
- PaperInput: `backups/MF2033k6lC/v2/paper-input/others/paper.json`
- PaperInput SHA-256: `89fcc578efcc840daa9c4e0698943314f794e096e176c067dbbd6e603d42ea66`
- Baseline commit: `4e8eea349ad0899299e952c5bdaa9131bc73c17a`
- Effective config: `fixtures/experiments/run_a/effective-config.json`
- CLI overrides: `--max-rounds 1 --max-concurrency 1`

The source PaperInput was already frozen and hash-pinned during phase 1, so it
is referenced in place instead of duplicating 180 KB into a second path. Run A
does not invoke MinerU. The snapshot contains no credential values; it records
only the credential environment-variable name. No business code, prompt, input,
or configuration may change between this commit and the single Run A execution.
