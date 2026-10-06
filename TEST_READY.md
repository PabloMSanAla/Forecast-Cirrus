# TEST_READY: End-to-End Verification Suite Ready

**Date:** 2026-09-04  
**Author:** `teamwork_preview_test_writer`  
**Milestone:** `E2E Testing Track`  
**Status:** **READY FOR EXECUTION**  

---

## 1. Executive Summary

The automated end-to-end verification harness and test suite for the FORECAST pipeline (`lc` and `df` modules) is fully implemented, verified, and operational in `tests/`.

All test scripts are self-contained, Darwin-aware, strictly opaque-box (testing specifications rather than internal implementation details), and mapped directly to user requirements R1 through R4.

---

## 2. Test Harness Inventory

The test harness suite comprises five modular tools located in `/Users/pmsanch1/code/FORECAST/tests/`:

| File | Type | Description |
|---|---|---|
| `tests/verify_md5.py` | Python 3 | Compares candidate outputs against baseline files and checks against exact authoritative MD5 checksums. |
| `tests/monitor_rss.py` | Python 3 | Darwin-aware memory monitor executing target commands under strict memory ceilings (4GB, 8GB, 16GB) and failing with exit code 3 upon breach. |
| `tests/benchmark_speedup.py` | Python 3 | Measures single-core wall-clock time and verifies that speedup is $\ge 20\%$ against recorded or live baselines. |
| `tests/test_cli.py` | Python 3 | Exercises CLI argument parsing, 0-indexed vs 1-indexed plane logic, and validation against `planes_list.txt`. |
| `tests/run_e2e_tests.sh` | Bash | Master runner executing all 4 test tiers, producing colored formatted summary reports and returning proper exit codes. |

---

## 3. Requirement & Feature Coverage Matrix

| Req | Feature | Description | Verifying Test Script | Test Tier | Expected Result |
| :---: | :---: |---|---|:---:|:---:|
| **R1** | **F2, F6** | **RAM Awareness & Ceiling Enforcement** (4GB, 8GB, 16GB) | `tests/monitor_rss.py` | T1, T2, T3 | Peak RSS strictly $\le$ limit; zero OOMs; breach triggers exit code 3 |
| **R2** | **F3, F7** | **Single-Core Speedup ($\ge 20\%$)** (No internal threading/OpenMP) | `tests/benchmark_speedup.py` | T1, T4 | Wall-clock execution time reduction $\ge 20\%$ vs baseline |
| **R3** | **F1, F5** | **CLI Interface & Plane Validation** (`<snapshot> <plane>`) | `tests/test_cli.py` | T1, T2, T3 | Valid pairs accepted; invalid pairs rejected immediately with exit code 1 |
| **--** | **F4, F8** | **Bit-Exact Correctness** (100% MD5 match on test planes) | `tests/verify_md5.py` | T1, T4 | 6/6 test plane files match baseline MD5 checksums byte-for-byte |
| **R4** | **F10** | **Audit Trail & Tracking Infrastructure** | `CHANGELOG.md`, `performance_history.csv` | T3 | Performance and RAM metrics logged across test runs |

---

## 4. Test Planes & Authoritative Reference Hashes

Validation is conducted on Rows 1, 2, and 4 from `/Volumes/PMSAdrive/pmsa/storage/TNG/optimization/planes_list.txt`:

| Row in `planes_list.txt` | Snapshot | Plane Index | Output Catalog File | Authoritative MD5 Checksum |
| :---: | :---: | :---: |---|---|
| **Row 1** | `98` | `0` | `coords.lc.98_0.txt` | `79ac9efb68c8ce6e08b1c7c09dd887ab` |
| **Row 2** | `98` | `1` | `coords.lc.98_1.txt` | `b1fc04316bb7a955d4f5df47a90628f7` |
| **Row 4** | `98` | `3` | `coords.lc.98_3.txt` | `9f9ff464b433c58f4104881a0efaa748` |
| **Row 1** | `98` | `0` | `flux.df.98_0.txt` | `a9eb9b4aad5e6e65bc220b462005f2bd` |
| **Row 2** | `98` | `1` | `flux.df.98_1.txt` | `cb8cdb62e2bf14bcbd6ff4c813044d80` |
| **Row 4** | `98` | `3` | `flux.df.98_3.txt` | `acbbb175ac0052dec2808c583b4a0d7d` |

---

## 5. Verification Runner Instructions

### Primary Test Command
To run the complete automated test suite across all 4 tiers:
```bash
bash tests/run_e2e_tests.sh
```

### Tier-Specific Execution Commands
```bash
# Tier 1 - Feature Coverage:
bash tests/run_e2e_tests.sh --tier 1

# Tier 2 - Boundary & Corner Cases:
bash tests/run_e2e_tests.sh --tier 2

# Tier 3 - Cross-Feature Combinations:
bash tests/run_e2e_tests.sh --tier 3

# Tier 4 - Real-World Application Scenarios:
bash tests/run_e2e_tests.sh --tier 4
```

### Module Developer Quick Checks

#### For LC Developer (`worker_lc_1`):
```bash
# 1. Verify CLI argument parsing & plane validation:
python3 tests/test_cli.py --bin ./lc/executable_lc

# 2. Verify peak RSS memory ceiling (4 GB):
python3 tests/monitor_rss.py --ceiling-gb 4.0 -- ./lc/executable_lc 98 0 4.0

# 3. Verify single-core speedup (>= 20%):
python3 tests/benchmark_speedup.py --module lc --plane 0 -- ./lc/executable_lc 98 0

# 4. Verify bit-exact MD5 match against baseline:
python3 tests/verify_md5.py --module lc --planes 0,1,3
```

#### For DF Developer (`worker_df_1`):
```bash
# 1. Verify CLI argument parsing & plane validation:
python3 tests/test_cli.py --bin ./df/executable_df

# 2. Verify peak RSS memory ceiling (4 GB):
python3 tests/monitor_rss.py --ceiling-gb 4.0 -- ./df/executable_df 98 1 4.0

# 3. Verify single-core speedup (>= 20%):
python3 tests/benchmark_speedup.py --module df --plane 1 -- ./df/executable_df 98 1

# 4. Verify bit-exact MD5 match against baseline:
python3 tests/verify_md5.py --module df --planes 0,1,3
```

---

## 6. Verification Status

- **Harness Code Quality:** Verified clean Python 3.13/3.14 and Bash syntax.
- **Baseline Integrity:** `tests/verify_md5.py --baseline-only` passed with 6/6 matching files.
- **Darwin Memory Accounting:** Verified on Apple Silicon `arm64-apple-darwin25.6.0` (`ru_maxrss` in bytes).
- **Master Runner Execution:** Ran `tests/run_e2e_tests.sh` with 10 Passed, 0 Failed, 1 Skipped (awaiting M1/M2 pipeline execution).
