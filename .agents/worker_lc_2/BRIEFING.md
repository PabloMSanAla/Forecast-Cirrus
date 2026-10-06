# BRIEFING — 2026-09-04T22:10:00Z

## Mission
Implement Milestone 1 integrity remediation, CLI argument validation, multi-tier config path resolution, and missing snapshot exit handling in the LC module.

## 🔒 My Identity
- Archetype: teamwork_preview_worker
- Roles: implementer, qa, specialist
- Working directory: /Users/pmsanch1/code/FORECAST/.agents/worker_lc_2
- Original parent: b38d576a-5afe-4d9d-876c-34d52200ddf0
- Milestone: Milestone 1 Iteration 2 (LC Module Optimization & Integrity Remediation)

## 🔒 Key Constraints
- DO NOT CHEAT: No hardcoded test results, expected outputs, or dummy/facade implementations.
- Write ownership: Exclusively own `/Users/pmsanch1/code/FORECAST/lc/` (`main_lc.cpp`, `functions.cpp`, `functions.h`, `readTNGParticle.cpp`, `Makefile`, `lc.ini`), `CHANGELOG.md`, `docs/performance_history.csv`, and `tests/verify_md5.py`.
- DO NOT modify any files in `df/`.
- Maintain real state and genuine logic.

## Current Parent
- Conversation ID: b38d576a-5afe-4d9d-876c-34d52200ddf0
- Updated: 2026-09-04T22:08:36Z

## Task Summary
- **What to build**: 
  1. Remove hardcoded test constants & branch (`oob_cmz`, `oob_np`, conditional check `snap==98 && plane==1`) in `lc/main_lc.cpp` and implement clean bounds handling.
  2. Update `tests/verify_md5.py` to accept uncorrupted hash (`5bfe39e8774c78ddf1eaa0d82e427637`) alongside legacy corrupted hash (`b1fc04316bb7a955d4f5df47a90628f7`).
  3. Enforce CLI argument bounds (`argc < 3 || argc > 4`) with exit code 1.
  4. Multi-tier config resolution for `lc.ini` and `planes_list.txt` in `functions.cpp` and `main_lc.cpp`.
  5. Clean exit code 2 on missing HDF5 snapshot data.
  6. Verify across test planes (0, 1, 3) under 4GB ceiling, run e2e and CLI tests, update CHANGELOG and performance history.
- **Success criteria**:
  - Zero hardcoding / integrity violations in `lc/main_lc.cpp` (VERIFIED: 0 matches for oob_cmz, oob_np, target_snap == 98).
  - CLI tests pass 18/18 (100% in strict mode).
  - Config resolution is directory-agnostic (verified from repo root).
  - Missing snapshot exits cleanly with code 2.
  - Bit-exact verification passes for planes 0, 1, 3 (100% MD5 match).
  - All documentation (`CHANGELOG.md`, `docs/performance_history.csv`, `report.md`, `handoff.md`) complete.
- **Interface contracts**: `/Users/pmsanch1/code/FORECAST/.agents/teamwork_preview_orchestrator_1/PROJECT.md`
- **Code layout**: `/Users/pmsanch1/code/FORECAST/.agents/teamwork_preview_orchestrator_1/PROJECT.md` § Code Layout

## Key Decisions Made
- Clean bounds zero-filling: `cmz_out = (i < (int)CMzsh.size()) ? CMzsh[i] : 0.0;` and `np_out = (i < (int)NpshTNG.size()) ? NpshTNG[i] : 0.0;` successfully deployed; all hardcoded arrays removed.
- Multi-tier resolution implemented: `getenv("FORECAST_LC_INI")`, `./lc.ini`, `lc/lc.ini`, `/Users/pmsanch1/code/FORECAST/lc/lc.ini`, and fallback, plus `FORECAST_OUTPUT_DIR` support.
- Snapshot existence pre-check implemented alongside `H5::Exception::dontPrint()` and `catch (const H5::Exception& e)` calling `exit(2)` in `main_lc.cpp` and `readTNGParticle.cpp`.

## Artifact Index
- `/Users/pmsanch1/code/FORECAST/.agents/worker_lc_2/report.md` — Final worker report
- `/Users/pmsanch1/code/FORECAST/.agents/worker_lc_2/handoff.md` — 5-component handoff report

## Change Tracker
- **Files modified**:
  - `lc/main_lc.cpp`: Removed hardcoded branches, enforced CLI arg bounds, added snapshot pre-check & exception wrapper, multi-tier planes_list.txt resolution.
  - `lc/functions.cpp`: Added multi-tier lc.ini resolution and output directory normalization.
  - `lc/readTNGParticle.cpp`: Added try/catch exit(2) around H5File opens (readHeader, readStars, readFof, readOffset, readGAS).
  - `tests/verify_md5.py`: Added acceptable hash 5bfe39e8774c78ddf1eaa0d82e427637 for coords.lc.98_1.txt, documented ASLR root cause.
  - `CHANGELOG.md`: Appended structured audit record per change_tracker skill.
  - `docs/performance_history.csv`: Appended verified benchmark and speedup records.
- **Build status**: PASS (`make -C lc clean && make -C lc` succeeds cleanly)
- **Pending issues**: None. All tasks completed and verified.

## Quality Status
- **Build/test result**: PASS. `test_cli.py` 18/18 (100%), `run_e2e_tests.sh` 11/11 (100%), `verify_md5.py` all planes PASS.
- **Lint status**: 0 violations
- **Tests added/modified**: `tests/verify_md5.py` updated to accept clean uncorrupted hash alongside legacy hash.

## Loaded Skills
- **Source**: `/Users/pmsanch1/code/FORECAST/.agents/skills/change_tracker/SKILL.md`
- **Local copy**: `/Users/pmsanch1/code/FORECAST/.agents/worker_lc_2/skills/change_tracker/SKILL.md`
- **Core methodology**: Human-readable audit trail of every modification, rationale, implementation details, measured impact (performance/RAM deltas), and structured changelog management.
