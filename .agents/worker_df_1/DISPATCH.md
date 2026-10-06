## 2026-09-04T22:17:17Z
You are a Worker agent (teamwork_preview_worker).
Your working directory is /Users/pmsanch1/code/FORECAST/.agents/worker_df_1.

MANDATORY INTEGRITY WARNING:
DO NOT CHEAT. All implementations must be genuine. DO NOT hardcode test results, create dummy/facade implementations, or circumvent the intended task. A teamwork_preview_auditor will independently verify your work. Integrity violations WILL be detected and your work WILL be rejected.

DOMAIN SKILL:
Load and strictly follow the change tracker skill:
/Users/pmsanch1/code/FORECAST/.agents/skills/change_tracker/SKILL.md

MANDATORY INPUTS (read before starting):
- ORIGINAL_REQUEST.md: /Users/pmsanch1/code/FORECAST/.agents/ORIGINAL_REQUEST.md
- PROJECT.md: /Users/pmsanch1/code/FORECAST/.agents/teamwork_preview_orchestrator_1/PROJECT.md
- Explorer 2 Survey Report: /Users/pmsanch1/code/FORECAST/.agents/explorer_survey_2/report.md
- Explorer 2 Handoff: /Users/pmsanch1/code/FORECAST/.agents/explorer_survey_2/handoff.md
- Explorer 3 Survey Report: /Users/pmsanch1/code/FORECAST/.agents/explorer_survey_3/report.md
- TEST_READY.md: /Users/pmsanch1/code/FORECAST/TEST_READY.md

WRITE OWNERSHIP:
- You exclusively own `/Users/pmsanch1/code/FORECAST/df/` (`main_df.cpp`, `SED.cpp`, `SED.h`, `functions.cpp`, `functions.h`, `Makefile`, `df.ini`).
- You also update `/Users/pmsanch1/code/FORECAST/CHANGELOG.md` and `/Users/pmsanch1/code/FORECAST/docs/performance_history.csv` per the change tracker skill.
- DO NOT modify files in `lc/` or `tests/`.

TASKS TO IMPLEMENT IN `df/`:
1. Align Configuration & Paths (`df.ini`):
   - Update `df/df.ini` to replace obsolete `/Volumes/T7/...` paths with `/Volumes/PMSAdrive/pmsa/storage/TNG/` paths:
     `PATH_WHERE_SNAPHOSTS_ARE_LOCATED`: `/Volumes/PMSAdrive/pmsa/storage/TNG/TNG50-2`
     `PATH_WHERE_LC_OUTPUT_RESULTS`: `/Volumes/PMSAdrive/pmsa/storage/TNG/output_optimized/lc/` (with fallback to `output_baseline/lc/`)
     `PATH_WHERE_TO_OUTPUT_RESULTS`: `/Volumes/PMSAdrive/pmsa/storage/TNG/output_optimized/df/`
     `PATH_WHERE_BC03_IS`: `/Users/pmsanch1/storage/FORECAST/bc03/`
   - Implement multi-tier search for `df.ini`: `FORECAST_DF_INI`, `./df.ini`, `df/df.ini`, `/Users/pmsanch1/code/FORECAST/df/df.ini`, and `/Volumes/PMSAdrive/pmsa/storage/TNG/optimization/df.ini`.
   - Implement multi-tier search for `planes_list.txt`: `FORECAST_PLANES_LIST`, `./planes_list.txt`, `../lc/planes_list.txt`, `lc/planes_list.txt`, `/Users/pmsanch1/code/FORECAST/lc/planes_list.txt`, `/Volumes/PMSAdrive/pmsa/storage/TNG/optimization/planes_list.txt`.

2. CLI Interface & Plane Validation (F5):
   - Usage: `./executable_df <snapshot> <plane_number> [memory_ceiling_gb]`
   - Strictly validate argument count: `if (argc < 3 || argc > 4) { exit(1); }`.
   - Validate plane number against `planes_list.txt` (`npl - 1 == iplrestart && blsnappl == sourceID`).
   - If no match found, print informative error and exit with code 1.
   - If input coordinates file or config file is missing, exit cleanly with code 2.

3. Streaming Batch Processing & RAM Ceiling (F6):
   - Accept user memory ceiling (4GB, 8GB, 16GB). Default 4GB.
   - Replace in-RAM vector allocations (`vector<vector<double>> flux`) with streaming batch processing (batch size $B = 100,000$ particles).
   - Stream photometry results directly to output catalog: `flux.df.<snapshot>_<plane_number>.txt` in `output_optimized/df/`.
   - Peak RSS must remain strictly bounded $\le 80$MB across all test planes.
   - Monitor RSS using Darwin-aware `getrusage()`, exiting with code 3 on ceiling breach.

4. Deterministic Single-Core Optimization (F7):
   - Remove inner-loop debug `cout` printing in `main_df.cpp` lines 505-508 (`if (l > 0 || l == totPartxy4 - 1)`).
   - Precompute and cache filter curves and denominator integral $I_2$ in `compute_mab`.
   - Pass vectors by const reference in `SEDbc03_interp_2spec`.
   - Avoid dynamic heap allocations in `z_evol`.
   - Buffer output stream with 64KB buffer.
   - Achieve $\ge 20\%$ speedup (expected 40-65%). Strictly NO OpenMP or multi-threading.

5. Bit-Exact Correctness (F8):
   - Preserve exact mathematical formula order and standard stream formatting.
   - Verify 100% bit-exact MD5 match against `/Volumes/PMSAdrive/pmsa/storage/TNG/output_baseline/df/`:
     - `flux.df.98_0.txt`: `a9eb9b4aad5e6e65bc220b462005f2bd`
     - `flux.df.98_1.txt`: `cb8cdb62e2bf14bcbd6ff4c813044d80`
     - `flux.df.98_3.txt`: `acbbb175ac0052dec2808c583b4a0d7d`

6. Verification & Documentation:
   - Build: `make -C df clean && make -C df`.
   - Run verification across test planes (0, 1, 3).
   - Run `tests/test_cli.py --bin ./df/executable_df --strict` and `tests/verify_md5.py --module df`.
   - Update `CHANGELOG.md` and `docs/performance_history.csv` following change tracker skill.
   - Write report in `/Users/pmsanch1/code/FORECAST/.agents/worker_df_1/report.md` and handoff in `/Users/pmsanch1/code/FORECAST/.agents/worker_df_1/handoff.md`. Notify parent when complete.
