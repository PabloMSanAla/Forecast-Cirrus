# Original User Request

## 2026-09-04T17:56:01Z

Improve the FORECAST pipeline (C/C++ hydrodynamical simulation processor) LC and DF modules to make them strictly RAM-aware (never exceeding user-defined memory limits such as 4GB, 8GB, and 16GB) as the primary focus, while optimizing single-core execution speed (targeting ≥20-30% reduction) without internal module parallelization, guaranteeing bit-exact deterministic outputs (100% MD5 match against baseline), and maintaining a complete change audit trail.

Working directory: /Users/pmsanch1/code/FORECAST
Integrity mode: development

## Requirements

### R1. RAM Awareness & Memory Footprint Control (Primary Focus)
Modify the `lc` and `df` modules to accept a user-specified memory ceiling (tested at 4GB, 8GB, and 16GB). The modules must estimate/monitor peak RSS and dynamically adapt processing chunk sizes, filter batch sizes, or streaming buffers so that the process never triggers an Out-of-Memory (OOM) killer and peak memory remains strictly within the limit.

### R2. Deterministic Performance Optimization (No Internal Parallelization)
Identify and eliminate computational and I/O bottlenecks in `lc` and `df` (e.g., buffered file I/O, avoiding redundant calculations, efficient data structures) to achieve ≥20% speedup. Do NOT introduce OpenMP or multi-threading inside the `lc` and `df` modules, as pipeline runs are parallelized externally per snapshot and plane.

### R3. CLI Interface and Plane Validation
Ensure executables accept `<snapshot> <plane_number>` as command-line arguments (e.g., `./executable_df 98 1`) and validate the plane number against `planes_list.txt` before execution.

### R4. Complete Audit Trail & Documentation
Log all decisions, code changes, performance deltas, and RAM deltas in `CHANGELOG.md` following the structured audit format, updating performance history metrics.

## Verification Resources & Environment

- **Conda Environment:** `conda activate forecast`
- **Configuration & Inputs:**
  - Config files: `lc.ini` and `df.ini` in `/Volumes/PMSAdrive/pmsa/storage/TNG/optimization/`
  - Plane list: `/Volumes/PMSAdrive/pmsa/storage/TNG/optimization/planes_list.txt`
  - Validation test planes: Rows 1, 2, and 4 (snapshots / plane numbers)
- **Baseline Outputs:** `/Volumes/PMSAdrive/pmsa/storage/TNG/output_baseline/` (read-only reference)
- **Optimized Outputs:** `/Volumes/PMSAdrive/pmsa/storage/TNG/output_optimized/`

## Acceptance Criteria

### Bit-Exact Correctness
- [ ] 100% MD5 checksum match between all files in `/Volumes/PMSAdrive/pmsa/storage/TNG/output_optimized/` and `/Volumes/PMSAdrive/pmsa/storage/TNG/output_baseline/` for the test planes.

### Memory Ceiling Enforcement
- [ ] Peak RSS stays strictly below or equal to the specified limits (tested with 4 GB, 8 GB, and 16 GB configurations).
- [ ] Zero Out-Of-Memory (OOM) crashes or process kills.

### Performance
- [ ] Execution wall-clock time reduced by at least 20% compared to baseline on test planes.
- [ ] No internal threading/OpenMP added inside `lc` and `df` modules.

### Documentation & Tracking
- [ ] `CHANGELOG.md` updated with exact actions, rationales, before/after wall-clock time, and before/after peak RAM metrics for every modification.
- [ ] A final `validation_report.md` generated summarizing pass/fail status across all test configurations.
