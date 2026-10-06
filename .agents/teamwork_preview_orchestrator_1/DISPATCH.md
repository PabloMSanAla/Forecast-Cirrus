# Dispatch Log

## 2026-09-04T17:56:55Z

You are the Project Orchestrator (teamwork_preview_orchestrator).

## Identity & Working Directory
- Identity: teamwork_preview_orchestrator
- Your working directory: /Users/pmsanch1/code/FORECAST/.agents/teamwork_preview_orchestrator_1
- Project workspace: /Users/pmsanch1/code/FORECAST
- Authoritative Original Request: /Users/pmsanch1/code/FORECAST/.agents/ORIGINAL_REQUEST.md
- Change tracker skill documentation: /Users/pmsanch1/code/FORECAST/.agents/skills/change_tracker/SKILL.md

## Mission
Orchestrate the full implementation, optimization, testing, verification, and audit documentation for the FORECAST pipeline LC and DF modules as specified in ORIGINAL_REQUEST.md.

## Core Requirements & Constraints
1. R1 - Strict RAM Awareness: `lc` and `df` modules must accept a user-specified memory ceiling (tested at 4GB, 8GB, and 16GB). The modules must estimate/monitor peak RSS and dynamically adapt processing chunk sizes, filter batch sizes, or streaming buffers so that the process never triggers an OOM killer and peak memory remains strictly within the limit.
2. R2 - Deterministic Single-Core Optimization: Identify and eliminate computational and I/O bottlenecks in `lc` and `df` to achieve >=20% speedup. NO internal threading/OpenMP inside `lc` and `df` modules (external parallelization is used per snapshot/plane).
3. R3 - CLI Interface & Plane Validation: Ensure executables accept `<snapshot> <plane_number>` as command-line arguments (e.g. `./executable_df 98 1`) and validate the plane number against `planes_list.txt` before execution.
4. R4 - Complete Audit Trail: Follow the change tracker guidelines in `/Users/pmsanch1/code/FORECAST/.agents/skills/change_tracker/SKILL.md`. Log all decisions, code changes, performance deltas, and RAM deltas in `CHANGELOG.md` and update `docs/performance_history.csv`. Generate a final `validation_report.md`.
5. Bit-Exact Correctness: 100% MD5 checksum match between all files in `/Volumes/PMSAdrive/pmsa/storage/TNG/output_optimized/` and `/Volumes/PMSAdrive/pmsa/storage/TNG/output_baseline/` for the test planes (Rows 1, 2, and 4 from `/Volumes/PMSAdrive/pmsa/storage/TNG/optimization/planes_list.txt`).
6. Environment: Conda environment `forecast`.

## Progress Tracking
Maintain your `BRIEFING.md` and `progress.md` continuously in your working directory (`/Users/pmsanch1/code/FORECAST/.agents/teamwork_preview_orchestrator_1/`).
When all work is verified and complete, notify Sentinel with a completion report.

## 2026-09-04T22:08:19Z

The rate limit quota reset has completed. Please resume orchestration, verify worker status, and proceed with project execution.

