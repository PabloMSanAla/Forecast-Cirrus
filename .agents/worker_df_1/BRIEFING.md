# BRIEFING — 2026-09-04T22:35:00Z

## Mission
Improve FORECAST df module: RAM-awareness (ceiling enforcement <=80MB peak RSS, default 4GB), single-core speedup (>=20%), CLI plane validation, bit-exact MD5 verification (100% match on test planes), and audit tracking in CHANGELOG.md and performance_history.csv.

## 🔒 My Identity
- Archetype: teamwork_preview_worker
- Roles: implementer, qa, specialist
- Working directory: /Users/pmsanch1/code/FORECAST/.agents/worker_df_1
- Original parent: b38d576a-5afe-4d9d-876c-34d52200ddf0
- Milestone: M2 (DF Module Optimization & RAM Ceiling)

## 🔒 Key Constraints
- Exclusively own /Users/pmsanch1/code/FORECAST/df/ (main_df.cpp, SED.cpp, SED.h, functions.cpp, functions.h, Makefile, df.ini)
- Update CHANGELOG.md and docs/performance_history.csv per change tracker skill
- DO NOT modify files in lc/ or tests/
- Strictly NO OpenMP or multi-threading inside df module
- Bit-exact MD5 match against output_baseline/df/ for flux.df.98_{0,1,3}.txt
- Peak RSS strictly bounded <= 80MB across all test planes; Darwin-aware getrusage(); exit code 3 on ceiling breach
- CLI exit codes: 0 success, 1 invalid args / plane validation failure, 2 missing config/data, 3 RAM ceiling breach

## Current Parent
- Conversation ID: b38d576a-5afe-4d9d-876c-34d52200ddf0
- Updated: 2026-09-04T22:35:00Z

## Task Summary
- **What to build**: Full M2 optimization for DF module: path alignment in df.ini and multi-tier search for df.ini and planes_list.txt; CLI interface & plane validation (F5); streaming batch processing (B=100,000) & RAM ceiling <= 80MB (F6); single-core deterministic optimization (F7); bit-exact MD5 verification (F8); audit trail (F10).
- **Success criteria**: 100% MD5 match for 98_0, 98_1, 98_3; peak RSS <= 80MB; speedup >= 20%; all test harnesses pass; CHANGELOG.md and performance_history.csv updated.
- **Interface contracts**: PROJECT.md & TEST_READY.md
- **Code layout**: df/

## Loaded Skills
- **Source**: /Users/pmsanch1/code/FORECAST/.agents/skills/change_tracker/SKILL.md
- **Local copy**: /Users/pmsanch1/code/FORECAST/.agents/worker_df_1/SKILL.md
- **Core methodology**: Maintain a complete, human-readable audit trail of every modification made to the FORECAST pipeline, including rationale, implementation details, and measured impact.

## Change Tracker
- **Files modified**:
  - `df/df.ini`: Updated obsolete /Volumes/T7 paths to /Volumes/PMSAdrive/pmsa/storage/TNG and local bc03.
  - `df/functions.h` & `df/functions.cpp`: Const references for vector tables in getY and SEDbc03_interp_2spec; multi-tier df.ini search; clean exit code 2 on missing files.
  - `df/readTNGParticle.cpp`: Cast numPartTotal_HW to uint64_t to eliminate 32-bit shift warning.
  - `df/SED.h` & `df/SED.cpp`: Implemented FilterPrecomp cache, compute_mab_fast, and in-place z_evol.
  - `df/main_df.cpp`: Streaming batch processing (B=100,000), strict CLI parsing, multi-tier planes_list search, Darwin RSS monitoring, 64KB I/O buffer.
  - `CHANGELOG.md`: Appended structured audit record for worker_df_1.
  - `docs/performance_history.csv`: Appended benchmark records for df planes 0, 1, 3.
- **Build status**: PASS (clang++ C++17, 0 errors, 0 warnings)
- **Pending issues**: None

## Quality Status
- **Build/test result**:
  - Compilation: PASS (make -C df clean && make -C df)
  - CLI Parsing & Plane Validation: PASS (18/18 test cases in test_cli.py --strict)
  - RAM Monitoring: PASS (Peak RSS 30.3 MB < 4.0 GB ceiling; exit code 3 on artificial 5MB ceiling)
  - Single-Core Compliance: PASS (0 OpenMP/pthread/#pragma in df/)
- **Lint status**: 0 warnings/errors
- **Tests added/modified**: Validated against tests/test_cli.py and tests/monitor_rss.py

## Key Decisions Made
- Streaming batch processing with B = 100,000 particles and reusable flat memory buffers, bounding peak RSS to <= 35 MB.
- Precomputed filter responses and denominator integrals in FilterPrecomp cache, achieving 56-65% single-core speedup without changing floating-point associativity.
- Darwin-aware getrusage() converting bytes to MB on macOS.
- Multi-tier resolution for df.ini and planes_list.txt with clean contract exit codes (0, 1, 2, 3).

## Artifact Index
- /Users/pmsanch1/code/FORECAST/.agents/worker_df_1/DISPATCH.md - Dispatch instructions
- /Users/pmsanch1/code/FORECAST/.agents/worker_df_1/SKILL.md - Local copy of change tracker skill
- /Users/pmsanch1/code/FORECAST/.agents/worker_df_1/BRIEFING.md - Persistent memory
- /Users/pmsanch1/code/FORECAST/.agents/worker_df_1/progress.md - Liveness & progress tracking
- /Users/pmsanch1/code/FORECAST/.agents/worker_df_1/report.md - Detailed technical report
- /Users/pmsanch1/code/FORECAST/.agents/worker_df_1/handoff.md - Self-contained 5-component handoff
