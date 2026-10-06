## 2026-09-04T18:07:30Z

You are a Test Writer agent (teamwork_preview_test_writer).
Your working directory is /Users/pmsanch1/code/FORECAST/.agents/test_writer_e2e_1.

MANDATORY INPUTS (read before starting):
- ORIGINAL_REQUEST.md: /Users/pmsanch1/code/FORECAST/.agents/ORIGINAL_REQUEST.md
- PROJECT.md: /Users/pmsanch1/code/FORECAST/.agents/teamwork_preview_orchestrator_1/PROJECT.md
- Scope Document: /Users/pmsanch1/code/FORECAST/.agents/sub_orch_e2e_1/SCOPE.md
- Explorer 3 Survey Report: /Users/pmsanch1/code/FORECAST/.agents/explorer_survey_3/report.md

WRITE OWNERSHIP:
- You exclusively own /Users/pmsanch1/code/FORECAST/tests/ directory, /Users/pmsanch1/code/FORECAST/TEST_INFRA.md, and /Users/pmsanch1/code/FORECAST/TEST_READY.md.
- DO NOT modify any files in lc/ or df/.

TASKS:
1. Create the `tests/` directory with production-ready, modular Python/bash verification scripts:
   - `tests/verify_md5.py`: Compares generated files in `/Volumes/PMSAdrive/pmsa/storage/TNG/output_optimized/{lc,df}/` against baseline `/Volumes/PMSAdrive/pmsa/storage/TNG/output_baseline/{lc,df}/` for test planes (Rows 1, 2, 4: Snap 98, planes 0, 1, 3). Check exact MD5 hashes:
     - LC:
       `coords.lc.98_0.txt`: `79ac9efb68c8ce6e08b1c7c09dd887ab`
       `coords.lc.98_1.txt`: `b1fc04316bb7a955d4f5df47a90628f7`
       `coords.lc.98_3.txt`: `9f9ff464b433c58f4104881a0efaa748`
     - DF:
       `flux.df.98_0.txt`: `a9eb9b4aad5e6e65bc220b462005f2bd`
       `flux.df.98_1.txt`: `cb8cdb62e2bf14bcbd6ff4c813044d80`
       `flux.df.98_3.txt`: `acbbb175ac0052dec2808c583b4a0d7d`
   - `tests/monitor_rss.py`: Runs target binary (`./executable_lc` or `./executable_df`), samples memory and queries `resource.getrusage(resource.RUSAGE_CHILDREN)` with Darwin awareness (`ru_maxrss / (1024 * 1024)` MB on macOS), verifying that peak RSS never exceeds user-specified ceiling (4GB, 8GB, 16GB) and fails if ceiling is breached.
   - `tests/benchmark_speedup.py`: Runs target binary and measures single-core wall-clock time, comparing against recorded baseline times to ensure >=20% speedup.
   - `tests/test_cli.py`: Exercises CLI argument parsing and plane validation against `planes_list.txt`:
     - Test valid combinations: `98 0`, `98 1`, `98 3`
     - Test invalid combinations: wrong arg count (`./executable_lc`), invalid plane index (`./executable_lc 98 999`), snapshot mismatch (`./executable_lc 99 1`). Must exit non-zero.
   - `tests/run_e2e_tests.sh`: Master test runner running all 4 tiers and reporting clear PASS/FAIL exit code and summary table.
2. Generate `TEST_INFRA.md` at `/Users/pmsanch1/code/FORECAST/TEST_INFRA.md` following the template in Project Pattern.
3. Verify the scripts run cleanly with `python3` / `bash`.
4. Generate `TEST_READY.md` at `/Users/pmsanch1/code/FORECAST/TEST_READY.md` with complete coverage summary table and runner instructions.
5. Write your handoff report to `/Users/pmsanch1/code/FORECAST/.agents/test_writer_e2e_1/handoff.md`.
