# Claim, quote and scope comparison

## Fixed S1, three network-approved repeats

All three complete responses give the same ten `(work_id, feature_id, relation)` values and the same cited evidence IDs. Raw reasons are in each `summary-review.json`. All five 2PS comparisons cite the original abstract `ev_c8...`; all five WStream comparisons cite the original abstract `ev_6c...`. Seven registered Reader quotes were in each exact frozen request, but final feature relations did not cite them. The first sandbox attempt failed with EPERM and contributes no semantic judgment.

| Work | Features | Repeated relations | Quote-scope audit |
|---|---|---|---|
| 2PS | F1–F3 | `contradicted` | Reasons infer absence of Count-Min Sketch, heap and probabilistic constant-time query from other described structures or no mention. A scoped abstract alone does not prove absence across the method. **Unsupported-strength concern; full text not adjudicated here.** |
| 2PS | F4–F5 | `partially_supported` | Reasons identify edge assignment and low replication/memory aims, then limit equivalence to degree-based subgraph and load balancing details. Plausible local partial match, not independent ground truth. |
| WStream | F1–F2, F4 | `contradicted` | Reasons cite metadata/window methods and no mention of Count-Min Sketch, min-heap or degree-based subgraph ID. The abstract does not establish exclusive implementation. **Unsupported-strength concern.** |
| WStream | F3 | `unknown` | No constant-time mechanism in the cited abstract. Appropriate scope. |
| WStream | F5 | `supported` | Abstract explicitly describes efficient partitioning of large graphs with balanced partitions. Locally supported. |

Thus 3/3 completion and relation repeatability do not certify `contradicted` semantics. The concern is retained without tuning production code on this observed batch. Original quote lineage and broader prior audit: `docs/experiments/20260918_reviewer_grounding_transfer/claim-evidence-review.md`.

## Frozen MG holdouts

| Case | Output | Source scope and audit |
|---|---|---|
| NP-1 / `wrk_eba9d160fb1590c9de66938d` | Card and summary `reviewed/not_novel`; F1–F4 `supported` | The frozen 1,367-character abstract directly mentions fine-grained attention to structure-related bars, coarse-grained summarization of other bars, their combined roles, and over 3× longer sequences. These local matches are supported. |
| NP-2 / `wrk_2e2856efebb6106c4344fc13` | Card and summary `reviewed/partially_novel`; F1 `partially_supported`, F2–F4 `unknown` | The frozen 943-character abstract discusses structure, repetitions and segment similarity, while self-similarity matrix and specific selection/genre details are not established. Unknown avoids turning no mention into contradiction. |

Neither local Reader catalog had a full body. Case files, source hashes and material catalogs are in `fixtures/holdout-preflight.json` and `trials/holdout/`. Two cases are not a generalization estimate.

## Four frozen synthetic controls

`fixtures/synthetic-semantic-controls.json` registered texts and expected observations before calls 15–18. Each single-card run used the supplied Evidence quote; no Reader material was registered and no `review_evidence` read citation was generated. These controls test reasoning on supplied quotes, not Reader provenance.

| Control | Actual response | Compared with registered observation |
|---|---|---|
| Equivalent mechanism | `reviewed/not_novel`, F1 `supported` | Matches deadline bucketing and worker assignment across different terms. |
| Cache plus possible write-ahead log | `insufficient_evidence/semantic_evidence`, F1 `unknown` | Preserves uncertainty about logging despite the stated cache. |
| Baseline attribution | `insufficient_evidence/semantic_evidence`, F1 `unknown` | Does not attribute baseline compression to the author method. |
| Polling difference plus optional encryption | `reviewed/partially_novel`, F1 `partially_supported` | Recognizes scoped polling/push difference and leaves encryption unverified. |

The outcomes align with intended observations, but short authored texts and zero Reader reads limit external validity. They do not erase the S1 absence-to-contradiction concern.
