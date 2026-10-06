---
title: RAM Estimator & Controller
description: Predict and control the RAM usage of the FORECAST pipeline to prevent exceeding user-defined memory limits.
---

# Agent: RAM Estimator & Controller

## Goal
Prevent the FORECAST pipeline from exceeding the user-provided memory limit (passed via initial parameters) by predicting RAM usage before execution and adapting the processing strategy accordingly.

## Core Skills

### 1. HDF5 Snapshot Analysis
- Parse input simulation snapshots (`*.hdf5`) to count particles, subhalos, and dataset sizes.
- Use these metrics to estimate the in-memory footprint of particle catalogs.

### 2. Config-Driven Adaptation
- Read the user’s RAM limit from `config.ini` or environment variables.
- If estimated peak RSS > limit:
  - Reduce `FILTER_BATCH_SIZE` (process fewer spectral filters simultaneously).
  - Reduce `CHUNK_SIZE` (load fewer particles per I/O operation).
  - Toggle on "streaming mode" to write intermediate results to disk earlier.
- If estimated RSS < limit:
  - Keep default batch sizes for maximum throughput.

### 3. Runtime Monitoring (Fallback)
- If the pipeline still approaches the RAM limit during execution:
  - Trigger a graceful fallback: pause downstream modules, flush memory caches, and resume with smaller chunks.
  - Log the warning so the change_tracker can record it.

## Files to Modify or Read
- `forecast/config.ini` – Adjust `FILTER_BATCH_SIZE` and `CHUNK_SIZE`.
- `forecast/lc/main_lc.cpp` – Insert estimation hooks before particle loading.

## Success Criteria
- The pipeline never triggers an OOM (Out of Memory) killer.
- Peak RSS stays within 95% of the user-defined limit.