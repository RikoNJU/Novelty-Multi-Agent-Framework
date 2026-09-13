# Run A PaperInput fixture

This record freezes the input for Part 1 phase 2. It prepares Run A but does not
execute it.

| Field | Value |
|---|---|
| case_id | `MF2033k6lC-v2-paper-input` |
| paper_id | `MF2033k6lC` |
| repo-relative source path | `backups/MF2033k6lC/v2/paper-input/others/paper.json` |
| SHA-256 | `89fcc578efcc840daa9c4e0698943314f794e096e176c067dbbd6e603d42ea66` |
| primary entrypoint | `scripts/run_full_workflow_live.py` (`paper_input`) |

Selection reason: this is the repository's existing complete, reusable
PaperInput for the designated case. Pinning its repo-relative path and content
hash removes MinerU/parser variation from Run A without copying a 180 KB fixture
in this phase. Any byte change requires updating this record and treating the
input as a new fixture revision.

Run A must also freeze the effective application configuration. Its Runtime
Debug `summary.json` must show the path/hash above and a distinct `run_id`. Do
not use Full Pipeline `--resume` as a substitute and do not fix the known
Reviewer-to-final-report contract before collecting the baseline.
