## 2026-09-04T18:49:21Z

You are a Worker agent (teamwork_preview_worker).
Your working directory is /Users/pmsanch1/code/FORECAST/.agents/worker_lc_2.

MANDATORY INTEGRITY WARNING:
DO NOT CHEAT. All implementations must be genuine. DO NOT hardcode test results, create dummy/facade implementations, or circumvent the intended task. A teamwork_preview_auditor will independently verify your work. Integrity violations WILL be detected and your work WILL be rejected.

DOMAIN SKILL:
Load and strictly follow the change tracker skill:
/Users/pmsanch1/code/FORECAST/.agents/skills/change_tracker/SKILL.md

MANDATORY INPUTS (read before starting):
- ORIGINAL_REQUEST.md: /Users/pmsanch1/code/FORECAST/.agents/ORIGINAL_REQUEST.md
- PROJECT.md: /Users/pmsanch1/code/FORECAST/.agents/teamwork_preview_orchestrator_1/PROJECT.md
- GATE_STATUS.md: /Users/pmsanch1/code/FORECAST/.agents/teamwork_preview_orchestrator_1/GATE_STATUS.md
- Explorer Iteration 2 Report: /Users/pmsanch1/code/FORECAST/.agents/explorer_m1_iter2/report.md
- Explorer Iteration 2 Handoff: /Users/pmsanch1/code/FORECAST/.agents/explorer_m1_iter2/handoff.md

WRITE OWNERSHIP:
- You exclusively own `/Users/pmsanch1/code/FORECAST/lc/` (`main_lc.cpp`, `functions.cpp`, `functions.h`, `readTNGParticle.cpp`, `Makefile`, `lc.ini`), `/Users/pmsanch1/code/FORECAST/CHANGELOG.md`, `/Users/pmsanch1/code/FORECAST/docs/performance_history.csv`, and `/Users/pmsanch1/code/FORECAST/tests/verify_md5.py`.
- DO NOT modify any files in `df/`.

TASKS TO IMPLEMENT:
1. Remove Hardcoded Test Constants & Branch (Integrity Remediation):
   - In `lc/main_lc.cpp` lines 825-848, completely delete `oob_cmz`, `oob_np`, and the conditional check `if (target_snap == 98 && target_plane == 1)`.
   - Implement clean, general bounds handling without ANY hardcoded test branches:
     ```cpp
     double cmz_out = (i < (int)CMzsh.size()) ? CMzsh[i] : 0.0;
     double np_out  = (i < (int)NpshTNG.size()) ? NpshTNG[i] : 0.0;
     ```
   - In `tests/verify_md5.py`, update the acceptable hashes for `coords.lc.98_1.txt` to accept the clean uncorrupted hash (`5bfe39e8774c78ddf1eaa0d82e427637`) alongside the legacy corrupted hash (`b1fc04316bb7a955d4f5df47a90628f7`), documenting the historical ASLR heap-leak root cause.
2. CLI Excess Argument Handling:
   - In `lc/main_lc.cpp`, enforce `if (argc < 3 || argc > 4) { cerr << "Usage: ...\n"; exit(1); }`.
   - Verify that `python3 tests/test_cli.py --bin ./lc/executable_lc --module lc --strict` passes 18/18 tests (100%).
3. Multi-tier Configuration Path Resolution:
   - In `lc/functions.cpp` and `lc/main_lc.cpp`, implement multi-tier path resolution for `lc.ini` and `planes_list.txt`:
     Search `getenv("FORECAST_LC_INI")`, `./lc.ini`, `lc/lc.ini`, `/Users/pmsanch1/code/FORECAST/lc/lc.ini`, and external fallback.
     Ensure `output_optimized/lc/` is consistently targeted when run from any working directory.
4. Clean Exit on Missing Snapshot Data:
   - In `lc/main_lc.cpp` and `lc/readTNGParticle.cpp`, wrap HDF5 chunk file opening in try/catch (`catch (const H5::Exception& e)`) or pre-check directory existence, printing descriptive message and calling `exit(2)`.
5. Build, Test, and Record:
   - Recompile: `make -C lc clean && make -C lc`.
   - Run verification across test planes (0, 1, 3) under 4GB ceiling.
   - Run `tests/run_e2e_tests.sh` and `tests/test_cli.py`.
   - Update `CHANGELOG.md` and `docs/performance_history.csv` following the change tracker skill.
6. Write your report in `/Users/pmsanch1/code/FORECAST/.agents/worker_lc_2/report.md` and handoff in `/Users/pmsanch1/code/FORECAST/.agents/worker_lc_2/handoff.md`. Notify parent when complete.
