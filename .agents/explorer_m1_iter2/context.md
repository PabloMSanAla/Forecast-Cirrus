# Context: Explorer M1 Iteration 2

- Working directory: /Users/pmsanch1/code/FORECAST/.agents/explorer_m1_iter2
- Role: teamwork_preview_explorer
- Task: Technical investigation to resolve Reviewer/Challenger findings for LC module:
  1. Eliminate hardcoded test branch `target_snap == 98 && target_plane == 1` in `lc/main_lc.cpp` lines 825-844. Find a structural, non-hardcoded resolution for the out-of-bounds artifact while ensuring bit-exact MD5 compatibility.
  2. Fix CLI argument validation: reject `argc > 4` with exit code 1.
  3. Fix `lc.ini` path resolution: ensure outputs consistently write to `output_optimized/lc/`.
  4. Fix missing input data directory handling: catch HDF5 exception and exit with code 2 instead of SIGABRT.
