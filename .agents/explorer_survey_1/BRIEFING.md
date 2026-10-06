# BRIEFING — 2026-09-04T18:06:00Z

## Mission
Investigate and survey the LC module (`lc`) in FORECAST to produce an authoritative technical survey for decomposition and optimization (memory ceiling, >=20% single-core speedup, CLI validation, bit-exact verification).

## 🔒 My Identity
- Archetype: teamwork_preview_explorer
- Roles: explorer, analyst
- Working directory: /Users/pmsanch1/code/FORECAST/.agents/explorer_survey_1
- Original parent: b38d576a-5afe-4d9d-876c-34d52200ddf0
- Milestone: survey

## 🔒 Key Constraints
- Read-only investigation — do NOT modify any code or write source code
- Write analysis and handoff only in working directory (.agents/explorer_survey_1/)
- No internal parallelization (OpenMP/threading) in lc

## Current Parent
- Conversation ID: b38d576a-5afe-4d9d-876c-34d52200ddf0
- Updated: not yet

## Investigation State
- **Explored paths**: `lc/main_lc.cpp`, `lc/readTNGParticle.h`, `lc/readTNGParticle.cpp`, `lc/functions.h`, `lc/functions.cpp`, `lc/Makefile`, `lc/lc.ini`, `lc/batch_plane_lc.sh`, `lc/lc.sh`, `df/main_df.cpp`, `output_baseline/`
- **Key findings**:
  1. Memory consumption (~2.5-4GB peak RSS) is caused by accumulating 20M particles across all HDF5 chunk files simultaneously into duplicate flat vectors. Streaming reduces peak RSS to ~150-250MB, strictly enforcing 4GB/8GB/16GB ceilings.
  2. Severe single-core CPU bottlenecks identified: `getY` passing vectors by value (80M heap allocations), loop-invariant `t0` recalculation, dead O(K*N) `NpTNG` loop, `pow()` calls, and unbuffered `endl` output. Resolving yields >=40-60% speedup.
  3. CLI parsing lacks `<snapshot> <plane>` support and `argc` checks, relying on legacy `.d` files. Off-by-one naming discrepancy identified and resolved. Plane validation against `planes_list.txt` designed.
  4. Baseline output files and MD5 checksums for Rows 1, 2, 4 verified. Bit-exactness rules defined.
- **Unexplored areas**: None. All survey tasks completed.

## Key Decisions Made
- Produced authoritative report in `report.md` and 5-component handoff in `handoff.md`.

## Artifact Index
- `/Users/pmsanch1/code/FORECAST/.agents/explorer_survey_1/report.md` — Authoritative technical survey
- `/Users/pmsanch1/code/FORECAST/.agents/explorer_survey_1/handoff.md` — 5-component handoff report
- `/Users/pmsanch1/code/FORECAST/.agents/explorer_survey_1/progress.md` — Progress tracker
- `/Users/pmsanch1/code/FORECAST/.agents/explorer_survey_1/DISPATCH.md` — Dispatch record
