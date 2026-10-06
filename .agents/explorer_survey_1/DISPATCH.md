## 2026-09-04T17:58:00Z
You are an Explorer agent (teamwork_preview_explorer).
Your working directory is /Users/pmsanch1/code/FORECAST/.agents/explorer_survey_1.
You must read ORIGINAL_REQUEST.md before starting work: /Users/pmsanch1/code/FORECAST/.agents/ORIGINAL_REQUEST.md

OBJECTIVE:
Investigate and survey the LC module (`lc`) in /Users/pmsanch1/code/FORECAST to provide the authoritative technical survey for decomposition and optimization.

SCOPE BOUNDARIES:
- Read-only exploration and analysis. DO NOT modify any code or write source code.
- Write your analysis and handoff only in your working directory (.agents/explorer_survey_1/).

TASKS TO INVESTIGATE:
1. Map all source files, headers, build scripts/Makefiles related to the `lc` module.
2. Examine the current CLI parsing and plane validation logic in `lc`. How does it handle `<snapshot> <plane_number>`? How should validation against `planes_list.txt` be integrated?
3. Analyze memory consumption in `lc`: Where are memory allocations happening? What data structures hold simulation/particle/grid data? What drives peak RSS?
4. Analyze how user-specified memory ceilings (4GB, 8GB, 16GB) can be accepted, estimated/monitored (peak RSS), and how chunk sizes, filter batch sizes, or streaming buffers can dynamically adapt to prevent OOM.
5. Identify computation and I/O bottlenecks in `lc` (e.g. file reading/writing, memory copies, loop structures) that can yield >=20% single-core wall-clock speedup without any multi-threading or OpenMP.
6. Verify output generation: What output files are written, in what formats, and how bit-exactness (100% MD5 match against baseline) can be guaranteed.

OUTPUT REQUIREMENTS:
- Write your detailed findings in /Users/pmsanch1/code/FORECAST/.agents/explorer_survey_1/report.md.
- Write your handoff summary in /Users/pmsanch1/code/FORECAST/.agents/explorer_survey_1/handoff.md.
- Send a completion message back to parent when done.
