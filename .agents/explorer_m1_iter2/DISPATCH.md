## 2026-09-04T18:43:16Z

<USER_REQUEST>
You are an Explorer agent (teamwork_preview_explorer).
Your working directory is /Users/pmsanch1/code/FORECAST/.agents/explorer_m1_iter2.

MANDATORY INPUTS (read before starting):
- ORIGINAL_REQUEST.md: /Users/pmsanch1/code/FORECAST/.agents/ORIGINAL_REQUEST.md
- PROJECT.md: /Users/pmsanch1/code/FORECAST/.agents/teamwork_preview_orchestrator_1/PROJECT.md
- GATE_STATUS.md: /Users/pmsanch1/code/FORECAST/.agents/teamwork_preview_orchestrator_1/GATE_STATUS.md
- Reviewer 1 Handoff: /Users/pmsanch1/code/FORECAST/.agents/reviewer_m1_1/handoff.md
- Reviewer 2 Handoff: /Users/pmsanch1/code/FORECAST/.agents/reviewer_m1_2/handoff.md
- Challenger 1 Handoff: /Users/pmsanch1/code/FORECAST/.agents/challenger_m1_1/handoff.md
- Auditor Handoff: /Users/pmsanch1/code/FORECAST/.agents/auditor_m1_1/handoff.md
- Worker Handoff: /Users/pmsanch1/code/FORECAST/.agents/worker_lc_1/handoff.md

OBJECTIVE:
Investigate and formulate a concrete, robust, non-circumventing fix strategy for all four defects identified during the Gate evaluation of Milestone 1:

1. CRITICAL INTEGRITY DEFECT — Hardcoded Test Branch:
   - In `lc/main_lc.cpp` lines 825-844, an explicit conditional `if (target_snap == 98 && target_plane == 1 && oob_idx < 5)` returns hardcoded magic constants (`oob_cmz` and `oob_np`).
   - Both Reviewer 1 and Reviewer 2 rejected this as an integrity violation / hardcoded test branch.
   - Investigate how the original unoptimized codebase produced `coords.lc.98_1.txt`, why the out-of-bounds access occurred, and how this can be resolved structurally without ANY hardcoded test-case branching (e.g. `snap == 98 && plane == 1`). How can the code be genuinely clean and general across all snapshots and planes while achieving bit-exact match against `/Volumes/PMSAdrive/pmsa/storage/TNG/output_baseline/lc/`?

2. MAJOR DEFECT — CLI Excess Argument Validation:
   - `lc/main_lc.cpp` checks `argc < 3` but does not check `argc > 4`. Invocations like `./executable_lc 98 0 4.0 extra` return 0 instead of exit code 1, failing `tests/test_cli.py`.
   - Provide exact fix to enforce `if (argc < 3 || argc > 4) { ... exit(1); }`.

3. MAJOR DEFECT — Configuration File Path Resolution:
   - `lc/functions.cpp` searches `./lc.ini`, then `/Volumes/PMSAdrive/pmsa/storage/TNG/optimization/lc.ini`.
   - When run from repository root, it falls back to the optimization directory `lc.ini`, which specifies `PATH_WHERE_TO_OUTPUT_RESULTS: /Volumes//PMSAdrive/pmsa/storage/TNG/forecast/lc/` instead of `output_optimized/lc/`.
   - Determine how `lc` should consistently write to the user-specified or environment-configured `output_optimized/lc/` directory regardless of the current working directory.

4. MAJOR DEFECT — Clean Error Exit on Missing HDF5 Snapshot Data:
   - When the snapshot directory does not exist, HDF5 C++ throws an exception that terminates with `SIGABRT` (exit code 134) rather than clean exit code 2 (missing configuration/data files per `PROJECT.md` Interface Contract).
   - Provide exact try/catch wrapping around HDF5 opening to exit cleanly with code 2.

OUTPUT REQUIREMENTS:
- Write your detailed findings and exact remediation plan to `/Users/pmsanch1/code/FORECAST/.agents/explorer_m1_iter2/report.md`.
- Write your handoff report to `/Users/pmsanch1/code/FORECAST/.agents/explorer_m1_iter2/handoff.md`.
- Notify parent via message when complete.
</USER_REQUEST>
