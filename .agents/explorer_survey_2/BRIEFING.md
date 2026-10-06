# BRIEFING — 2026-09-04T18:05:00Z

## Mission
Investigate and survey the DF module (`df`) in FORECAST for RAM awareness, CLI/plane validation, single-core optimization, and bit-exact reproducibility.

## 🔒 My Identity
- Archetype: teamwork_preview_explorer
- Roles: explorer, investigator, analyst
- Working directory: /Users/pmsanch1/code/FORECAST/.agents/explorer_survey_2
- Original parent: b38d576a-5afe-4d9d-876c-34d52200ddf0
- Milestone: survey

## 🔒 Key Constraints
- Read-only investigation — do NOT implement or modify source code
- Strictly examine single-core speedup (no OpenMP or internal multi-threading)
- Memory ceilings (4GB, 8GB, 16GB) strictly enforced without OOM
- Bit-exactness (100% MD5 match against baseline) guaranteed

## Current Parent
- Conversation ID: b38d576a-5afe-4d9d-876c-34d52200ddf0
- Updated: 2026-09-04T18:05:00Z

## Investigation State
- **Explored paths**: `df/main_df.cpp`, `df/SED.h`, `df/SED.cpp`, `df/functions.h`, `df/functions.cpp`, `df/readTNGParticle.h`, `df/readTNGParticle.cpp`, `df/Makefile`, `df/df.sh`, `df/df.ini`, `files/`, `/Volumes/PMSAdrive/pmsa/storage/TNG/` (optimization, output_baseline, forecast).
- **Key findings**:
  1. Particle photometry is 100% independent across particles; streaming in 100k batches keeps peak RSS bounded at <=80 MB regardless of plane size (eliminating OOM on 4GB/8GB/16GB).
  2. Four computational bottlenecks identified yielding >=40-65% single-core speedup: removal of unintended inner-loop debug print (780k unbuffered flushes), caching filter invariants/integrals in `compute_mab`, zero-allocation table access in `SEDbc03_interp_2spec`, and in-place scaling in `z_evol`.
  3. Plane validation bug identified: missing plane match silently continues with uninitialized data; multi-tier path resolution and fail-fast validation designed.
  4. Output format and bit-exactness requirements verified: 14 space-separated columns, default stream precision, baseline MD5s recorded for test rows 1, 2, 4.
- **Unexplored areas**: None for DF module survey.

## Key Decisions Made
- Authored comprehensive `report.md` covering all 6 investigation tasks.
- Authored 5-component `handoff.md` adhering strictly to Handoff Protocol.

## Artifact Index
- /Users/pmsanch1/code/FORECAST/.agents/explorer_survey_2/report.md — Detailed survey report
- /Users/pmsanch1/code/FORECAST/.agents/explorer_survey_2/handoff.md — 5-component handoff summary
- /Users/pmsanch1/code/FORECAST/.agents/explorer_survey_2/progress.md — Liveness and progress tracker
- /Users/pmsanch1/code/FORECAST/.agents/explorer_survey_2/DISPATCH.md — Dispatch log
