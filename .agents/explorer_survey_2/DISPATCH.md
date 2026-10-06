## 2026-09-04T17:58:00Z

Investigate and survey the DF module (`df`) in /Users/pmsanch1/code/FORECAST to provide the authoritative technical survey for decomposition and optimization.

SCOPE BOUNDARIES:
- Read-only exploration and analysis. DO NOT modify any code or write source code.
- Write your analysis and handoff only in your working directory (.agents/explorer_survey_2/).

TASKS TO INVESTIGATE:
1. Map all source files, headers, build scripts/Makefiles related to the `df` module.
2. Examine the current CLI parsing and plane validation logic in `df`. How does it handle `<snapshot> <plane_number>`? How should validation against `planes_list.txt` be integrated?
3. Analyze memory consumption in `df`: Where are memory allocations happening? What data structures hold simulation/particle/grid data? What drives peak RSS?
4. Analyze how user-specified memory ceilings (4GB, 8GB, 16GB) can be accepted, estimated/monitored (peak RSS), and how chunk sizes, filter batch sizes, or streaming buffers can dynamically adapt to prevent OOM.
5. Identify computation and I/O bottlenecks in `df` (e.g. density field calculations, file reading/writing, memory layouts) that can yield >=20% single-core wall-clock speedup without any multi-threading or OpenMP.
6. Verify output generation: What output files are written, in what formats, and how bit-exactness (100% MD5 match against baseline) can be guaranteed.
