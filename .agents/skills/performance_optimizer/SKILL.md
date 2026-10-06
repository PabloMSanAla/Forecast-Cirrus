---
title: Performance Optimizer
description: Optimize the performance of the FORECAST pipeline by reducing execution time of critical modules while ensuring bit-exact results.
---
# Agent: Performance Optimizer

## Goal
Reduce execution time of the `lc`, `df` modules while guaranteeing **bit-exact** results compared to the original pipeline.

## Core Skills

### 1. Bottleneck Profiling (Static Analysis)
- Scan C++ source files to identify:
  - Large `for` loops over particles (`nParticles`) and filters (`nFilters`).
  - Slow ASCII file I/O (e.g., `fprintf`, `fopen` for catalog files).
  - Repeated calculations inside loops (e.g., redshift-dependent factors).

### 2. I/O Optimization
- Identify instances where the pipeline writes intermediate ASCII catalogs.
- Replace these with HDF5 binary writes (using the existing `H5Cpp.h` library).
- Implement buffered reading for snapshot files to reduce syscall overhead.

### 3. Algorithm Substitution (if safe)
- Replace O(N²) spatial neighbor searches with grid-based hashing or kd-tree lookups.
- **Condition:** Only apply if the floating-point rounding error is strictly identical (e.g., using the same summation order).

## Verification Constraint
- **Critical Rule:** After every optimization, the agent must verify that outputs remain unchanged. If a change alters results, the optimization must be reverted immediately.

- **Note:** Do not make parallelization inside the `lc` and `df` modules, as each module will be run in parallel for each plane number and snapshot. 

## Files to Modify
- `forecast/lc/functions.cpp` (spatial searches)
- `forecast/df/SED.cpp` (interpolation loops)
- `forecast/dc/functions.cpp` (dust attenuation)
- `forecast/postprocessing/create_image.cpp` (image generation I/O)

## Success Criteria
- Execution time drops by ≥ 30% per module.
- MD5 hashes of output catalogs remain identical to the baseline.