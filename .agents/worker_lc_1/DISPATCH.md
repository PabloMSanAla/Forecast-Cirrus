## 2026-09-04T18:07:30Z
You are a Worker agent (teamwork_preview_worker).
Your working directory is /Users/pmsanch1/code/FORECAST/.agents/worker_lc_1.

MANDATORY INTEGRITY WARNING:
DO NOT CHEAT. All implementations must be genuine. DO NOT hardcode test results, create dummy/facade implementations, or circumvent the intended task. A teamwork_preview_auditor will independently verify your work. Integrity violations WILL be detected and your work WILL be rejected.

DOMAIN SKILL:
Load and strictly follow the change tracker skill:
/Users/pmsanch1/code/FORECAST/.agents/skills/change_tracker/SKILL.md

MANDATORY INPUTS (read before starting):
- ORIGINAL_REQUEST.md: /Users/pmsanch1/code/FORECAST/.agents/ORIGINAL_REQUEST.md
- PROJECT.md: /Users/pmsanch1/code/FORECAST/.agents/teamwork_preview_orchestrator_1/PROJECT.md
- Scope Document: /Users/pmsanch1/code/FORECAST/.agents/sub_orch_m1_1/SCOPE.md
- Explorer 1 Survey Report: /Users/pmsanch1/code/FORECAST/.agents/explorer_survey_1/report.md
- Explorer 3 Survey Report: /Users/pmsanch1/code/FORECAST/.agents/explorer_survey_3/report.md

WRITE OWNERSHIP:
- You exclusively own `/Users/pmsanch1/code/FORECAST/lc/` files (`main_lc.cpp`, `functions.cpp`, `functions.h`, `readTNGParticle.cpp`, `readTNGParticle.h`, `Makefile`).
- You also update `/Users/pmsanch1/code/FORECAST/CHANGELOG.md` and `/Users/pmsanch1/code/FORECAST/docs/performance_history.csv` per the change tracker skill.
- DO NOT modify any files in df/ or tests/.

TASKS TO IMPLEMENT IN `lc/`:
1. CLI Interface & Plane Validation (F1):
   - Accept `./executable_lc <snapshot> <plane_number> [memory_ceiling_gb]`.
   - Remove dependency on reading `<argv[2]>.d` file! Parse snapshot and plane number directly from argv.
   - Resolve `planes_list.txt` path (check local `planes_list.txt`, then `/Volumes/PMSAdrive/pmsa/storage/TNG/optimization/planes_list.txt`).
   - Validate that snapshot and plane number match an entry in `planes_list.txt` (remember `argv[2]` is 0-indexed plane index `npl - 1`, corresponding to rows 1, 2, 4 having plane indices 0, 1, 3 for snapshot 98). If no match or invalid args, print an informative error and exit with non-zero code.
   - Fix output filename formatting so that 0-indexed plane index produces `coords.lc.<snap>_<plane>.txt` matching baseline (`coords.lc.98_0.txt`, `coords.lc.98_1.txt`, `coords.lc.98_3.txt`) in the configured output directory (`/Volumes/PMSAdrive/pmsa/storage/TNG/output_optimized/lc/`).
2. RAM Awareness & Streaming Chunk Processing (F2):
   - Accept user-specified memory ceiling (e.g. 4GB, 8GB, 16GB). Default to 4GB if not specified.
   - Refactor particle loading to stream HDF5 file-by-file / chunk-by-chunk: rather than loading all 20M particles of snapshot 98 into duplicate flat vectors simultaneously, process each chunk, filter star particles falling into the plane FoV, and retain only the lightcone particles.
   - Implement Darwin-aware RSS monitoring (`getrusage(RUSAGE_SELF)` returning bytes on macOS, divided by 1024*1024 for MB). Ensure peak RSS stays well under the memory ceiling (<250MB).
3. Deterministic Single-Core Performance Optimization (F3):
   - In `functions.cpp` and `main_lc.cpp`: change `getY` parameter signatures to `const std::vector<double>&` to eliminate tens of millions of heap allocations/copies.
   - Hoist invariant `t0 = getY(z_tlist, age_tlist, zsim)` out of the particle loop (computed once, not 20M times).
   - Eliminate the unused dead loop in `main_lc.cpp` lines 1035-1044 that counts `NpTNG`.
   - Replace `pow(..., 2)` with inline multiplication (`dx * dx`).
   - Optimize center-of-mass calculation.
   - Buffer output stream and replace per-line `std::endl` flushes with `\n`.
   - Ensure NO internal OpenMP or multi-threading is introduced.
4. Bit-Exact Correctness (F4):
   - Preserve exact mathematical operations, variable types, and particle order.
   - Target 100% MD5 match against `/Volumes/PMSAdrive/pmsa/storage/TNG/output_baseline/lc/`:
     - `coords.lc.98_0.txt`: `79ac9efb68c8ce6e08b1c7c09dd887ab`
     - `coords.lc.98_1.txt`: `b1fc04316bb7a955d4f5df47a90628f7`
     - `coords.lc.98_3.txt`: `9f9ff464b433c58f4104881a0efaa748`
5. Verification & Audit:
   - Build using `make -C lc clean && make -C lc`.
   - Execute test runs on planes 0, 1, 3 under memory limits (4GB, 8GB, 16GB).
   - Verify MD5 matches baseline.
   - Measure and record before/after wall-clock time and peak RSS.
   - Append structured entry to `CHANGELOG.md` and record metrics in `docs/performance_history.csv`.
6. Output:
   - Write completion report in `/Users/pmsanch1/code/FORECAST/.agents/worker_lc_1/report.md`.
   - Write handoff report in `/Users/pmsanch1/code/FORECAST/.agents/worker_lc_1/handoff.md`.
