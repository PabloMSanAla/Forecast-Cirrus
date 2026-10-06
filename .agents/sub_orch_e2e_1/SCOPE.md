# Scope: E2E Testing Track

## Mission
Design, implement, and verify a comprehensive, opaque-box, requirement-driven E2E test suite for the FORECAST pipeline LC and DF modules, and publish `TEST_READY.md`.

## Requirements & Methodology
- Opaque-box testing based strictly on `ORIGINAL_REQUEST.md` and user requirements (not internal implementation details).
- 4-Tier Test Case Design:
  - **Tier 1 - Feature Coverage**: Test each feature in isolation across `lc` and `df`.
  - **Tier 2 - Boundary & Corner Cases**: CLI argument validation, invalid plane indices, nonexistent snapshots, empty/boundary inputs, Darwin-aware RSS limits.
  - **Tier 3 - Cross-Feature Combinations**: Pairwise interactions (e.g. CLI argument parsing with 4GB/8GB/16GB memory ceilings, pipeline chaining from LC coordinates into DF fluxes).
  - **Tier 4 - Real-World Application Scenarios**: Full pipeline runs on test planes (Rows 1, 2, and 4: Snap 98, planes 0, 1, 3).
- Test Harness Tools to Build in `tests/`:
  1. `verify_md5.py`: Bit-exact comparison against `/Volumes/PMSAdrive/pmsa/storage/TNG/output_baseline/` for `coords.lc.98_{0,1,3}.txt` and `flux.df.98_{0,1,3}.txt`.
  2. `monitor_rss.py`: Run target executables under memory ceilings (4GB, 8GB, 16GB), sampling RSS and querying `getrusage(RUSAGE_CHILDREN)` with Darwin byte conversion (`ru_maxrss / 1024 / 1024` for MB). Fail if peak RSS exceeds ceiling or if exit status indicates OOM/crash.
  3. `benchmark_speedup.py`: Measure single-core wall-clock time against baseline; verify $\ge 20\%$ speedup.
  4. `test_cli.py`: Verify `./executable_lc` and `./executable_df` argument parsing: reject wrong arg count, reject planes not in `planes_list.txt`, reject snapshot/plane mismatches.
  5. `run_e2e_tests.sh`: Unified runner executing all test tiers and reporting summary results.
- Published Signal:
  - `TEST_READY.md` at project root with test commands, tier breakdown, and coverage checklist.

## Code Layout Ownership
- Exclusively owns `tests/` directory and `TEST_INFRA.md` / `TEST_READY.md`.
- Must NOT modify `lc/*.cpp`, `lc/*.h`, `df/*.cpp`, `df/*.h`.

## Reference Inputs
- `ORIGINAL_REQUEST.md`: `/Users/pmsanch1/code/FORECAST/.agents/ORIGINAL_REQUEST.md`
- `PROJECT.md`: `/Users/pmsanch1/code/FORECAST/.agents/teamwork_preview_orchestrator_1/PROJECT.md`
- Explorer 3 Report: `/Users/pmsanch1/code/FORECAST/.agents/explorer_survey_3/report.md`
