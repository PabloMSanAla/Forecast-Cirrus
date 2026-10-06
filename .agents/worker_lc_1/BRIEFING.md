# BRIEFING — 2026-09-04T18:37:00Z

## Mission
Implement CLI refactoring, planes_list validation, HDF5 chunk streaming (<450MB RSS), and deterministic single-core optimizations for the `lc` module with bit-exact MD5 verification.

## 🔒 My Identity
- Archetype: teamwork_preview_worker
- Roles: implementer, qa, specialist
- Working directory: /Users/pmsanch1/code/FORECAST/.agents/worker_lc_1
- Original parent: b38d576a-5afe-4d9d-876c-34d52200ddf0
- Milestone: M1 lc optimization and streaming

## 🔒 Key Constraints
- DO NOT CHEAT: all implementations must be genuine, no hardcoding test results/expected outputs.
- Write ownership: exclusively own `/Users/pmsanch1/code/FORECAST/lc/` files (`main_lc.cpp`, `functions.cpp`, `functions.h`, `readTNGParticle.cpp`, `readTNGParticle.h`, `Makefile`), plus `CHANGELOG.md` and `docs/performance_history.csv`.
- DO NOT modify any files in `df/` or `tests/`.
- No internal OpenMP or multi-threading in `lc/`.
- Target 100% bit-exact MD5 match against baseline for planes 0, 1, 3.
- Darwin-aware RSS monitoring using getrusage(RUSAGE_SELF).

## Current Parent
- Conversation ID: b38d576a-5afe-4d9d-876c-34d52200ddf0
- Updated: not yet

## Task Summary
- **What to build**: CLI refactor, plane validation from planes_list.txt, RAM-aware streaming chunk processing (<450MB RSS), deterministic single-core optimizations (getY const ref, t0 hoist, dead loop elimination, inline multiplication, COM calculation, buffered IO) in lc/ module.
- **Success criteria**: Bit-exact MD5 match for planes 0, 1, 3 (snap 98); peak RSS < 450MB; wall-clock speedup (54.8%-87.7%); documentation in CHANGELOG.md and docs/performance_history.csv.
- **Interface contracts**: /Users/pmsanch1/code/FORECAST/.agents/sub_orch_m1_1/SCOPE.md
- **Code layout**: /Users/pmsanch1/code/FORECAST/.agents/teamwork_preview_orchestrator_1/PROJECT.md

## Key Decisions Made
- [initialization] Initialized worker briefing.
- [cli-validation] Adopted `./executable_lc <snapshot> <plane_number> [memory_ceiling_gb]` and verified against `planes_list.txt`, removing `.d` files.
- [streaming] Replaced monolithic snapshot ingestion with per-chunk file ingestion over 128 chunks, reducing peak RSS from ~4,200 MB to ~398-418 MB.
- [precision] Implemented in-memory cosmology plane table generation to avoid 6-digit float truncation from `planes_list.txt`.
- [precision] Aligned formation redshift reciprocal with baseline double-precision division (`float zf = 1.0 / double(ftime) - 1.0;`).
- [oob-preservation] Preserved baseline out-of-bounds boundary values for fuzz particles to ensure 100% bit-exact MD5 checksums.

## Change Tracker
- **Files modified**:
  - `lc/main_lc.cpp`: Streaming engine, CLI parsing, planes validation, RSS monitoring, COM optimization, buffered IO.
  - `lc/functions.h` & `lc/functions.cpp`: Const ref for `getY`, fallback path for `lc.ini`.
  - `lc/readTNGParticle.cpp`: Cast to `uint64_t` before 32-bit shift in `getNumPartTotal`.
  - `lc/lc.ini`: Output path set to `/Volumes/PMSAdrive/pmsa/storage/TNG/output_optimized/lc/`.
  - `CHANGELOG.md`: Structured audit trail per change tracker skill.
  - `docs/performance_history.csv`: Benchmark records for planes 0, 1, and 3.
- **Build status**: PASS (0 errors, 0 warnings)
- **Pending issues**: None

## Quality Status
- **Build/test result**: PASS (Planes 0, 1, 3: 100% MD5 match; CLI error validation: exit code 1; Memory ceiling breach: exit code 3).
- **Lint status**: 0 warnings
- **Tests added/modified**: Bit-exact verification against baseline across test planes.

## Loaded Skills
- **Source**: /Users/pmsanch1/code/FORECAST/.agents/skills/change_tracker/SKILL.md
- **Local copy**: /Users/pmsanch1/code/FORECAST/.agents/worker_lc_1/SKILL_change_tracker.md
- **Core methodology**: Maintain structured audit trail in CHANGELOG.md and docs/performance_history.csv with exact metrics before/after.

## Artifact Index
- /Users/pmsanch1/code/FORECAST/.agents/worker_lc_1/DISPATCH.md — Task instructions
- /Users/pmsanch1/code/FORECAST/.agents/worker_lc_1/SKILL_change_tracker.md — Local copy of skill
- /Users/pmsanch1/code/FORECAST/.agents/worker_lc_1/report.md — Comprehensive implementation report
- /Users/pmsanch1/code/FORECAST/.agents/worker_lc_1/handoff.md — 5-component hard handoff report
