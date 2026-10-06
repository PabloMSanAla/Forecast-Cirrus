---
title: Testing & Validation
description: Ensure that the optimized FORECAST pipeline produces bit-exact outputs while adhering to RAM constraints.
---

# Agent: Testing & Validation

## Goal
Guarantee that the optimized FORECAST pipeline produces **exactly the same outputs** as the original, while respecting the RAM constraints.

## Core Skills

### 1. Baseline Establishment
- Run the original, unmodified FORECAST pipeline on a standardized test dataset (e.g., IllustrisTNG Snapshot 33, 3 filters).
- Record:
  - Wall-clock time per module (`lc`, `df`, `dc`, `igm`).
  - Peak Resident Set Size (RSS) per module.
  - MD5 checksums for every output file (catalogs, images, logs).

### 2. Real-Time RAM Monitoring
- Execute the pipeline while running a monitoring script in parallel.
- Use `/proc/[pid]/status` or `psutil` to poll RSS every 100ms.
- **Enforcement:** If RSS exceeds the user-defined limit, the agent sends a `SIGSTOP` to pause the process and logs the violation.

### 3. Bit-Exact Output Comparison
- After the optimized run, recursively compare the output directories.
- For every file present in both runs:
  - Compute MD5 hash.
  - If any hash differs, the test **FAILS**.
- Generate a diff report showing exactly which files are mismatched.

### 4. Regression Suite Management
- Maintain a set of test configurations:
  - Low RAM (4 GB), Medium RAM (8 GB), High RAM (32 GB).
  - Different field-of-view sizes (1, 4, 16 sq. arcmin).
- Run the full suite before any merge request is approved.


# FORECAST Test Specification

## Input Parameters
- follow the 'lc.ini' and 'df.ini' configuration files for input parameters stored in `/Volumes/PMSAdrive/pmsa/storage/TNG/optimization/`
- Use the planes_list.txt stored in `/Volumes/PMSAdrive/pmsa/storage/TNG/optimization/planes_list.txt`
- Only do validation tests on these specific plane numbers:

1   0.0108551   29.9082   35   0   98   0.01
2   0.0175277   35   69.6429   1   98   0.01
4   0.0418893   104.286   138.929   3   98   0.01

rows 1,2,4 inside `/Volumes/PMSAdrive/pmsa/storage/TNG/optimization/planes_list.txt`

- Conda environment: use the conda enviroment named `forecast` activated by:
  ```bash
  conda activate forecast
  ```
  before running any of the execution commands.



## RAM Limits to Validate
- 4 GB (stress test)
- 8 GB (standard)
- 16 GB (high)

Test ram limits with other plane numbers as well, like :

3   0.0290668   69.6429   104.286   2   98   0.01
20   0.239441   658.571   693.214   19   98   0.01
33   0.417019   1108.93   1143.57   32   98   0.01

although there is not a validation files for df module. 

## Execution Commands
- **Baseline:** `./forecast/bin/run_forecast_lc.sh --config tests/config_baseline_lc.ini`
- **Optimized:** `./forecast/bin/run_forecast_optimized_lc.sh --config tests/config_optimized_lc.ini`
- **Baseline:** `./forecast/bin/run_forecast_df.sh --config tests/config_baseline_df.ini`
- **Optimized:** `./forecast/bin/run_forecast_optimized_df.sh --config tests/config_optimized_df.ini`

## Output Directories
- Baseline outputs: `/Volumes/PMSAdrive/pmsa/storage/TNG/output_baseline/`
- Optimized outputs: `/Volumes/PMSAdrive/pmsa/storage/TNG/output_optimized/`

Do not modify the baseline outputs.

## Validation Criteria
1. All files in `/Volumes/PMSAdrive/pmsa/storage/TNG/output_baseline/` exist in `/Volumes/PMSAdrive/pmsa/storage/TNG/output_optimized/` and vice versa. Except for the RAM specific test that might not have df module outputs.
2. `md5sum` matches for every paired file.
3. Peak RSS logged during execution ≤ specified RAM limit.
4. Execution time reduced by at least 30% in the optimized version.

## Success Criteria
- `compare` mode returns `SUCCESS` (all hashes match) for all test configurations.
- Peak RAM never exceeds the specified limit.
- A validation report (`validation_report.md`) is generated summarizing pass/fail status.