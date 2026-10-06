# FORECAST Pipeline Verification & Test Infrastructure (`TEST_INFRA.md`)

## 1. Overview & Architecture

The FORECAST pipeline verification infrastructure provides an automated, requirement-driven, opaque-box test harness for validating the Lightcone (`lc`) and Dust-Free Photometry (`df`) simulation processing modules.

The test infrastructure enforces four non-negotiable requirements derived from `ORIGINAL_REQUEST.md`:
1. **Memory Footprint Control (Primary Focus)**: Zero Out-Of-Memory (OOM) events and strict adherence to memory ceilings (4 GB, 8 GB, 16 GB), accounting for macOS Darwin `ru_maxrss` byte-level semantics.
2. **Deterministic Performance Optimization**: $\ge 20\%$ single-core wall-clock reduction compared to baseline, without internal module multithreading or OpenMP.
3. **Bit-Exact Correctness**: 100% MD5 checksum match between candidate outputs in `output_optimized/` and reference baselines in `output_baseline/` for test planes.
4. **Robust CLI Argument Parsing & Plane Validation**: Robust validation of `<snapshot> <plane_number>` against `planes_list.txt`, with fail-fast non-zero exit codes on invalid arguments.

---

## 2. Test Harness Inventory (`tests/`)

The `tests/` directory contains modular Python 3 and Bash verification scripts designed to be executed both independently and orchestrated via the master test runner:

| Script | Type | Purpose | Primary Options |
|---|---|---|---|
| `tests/verify_md5.py` | Python 3 | Bit-exact output comparison against baseline & authoritative MD5 hashes | `--baseline-only`, `--module`, `--planes`, `--diff`, `--json` |
| `tests/monitor_rss.py` | Python 3 | Real-time Darwin-aware peak RSS monitoring and memory ceiling enforcement | `--ceiling-gb`, `--poll-interval`, `--kill-on-breach`, `--json` |
| `tests/benchmark_speedup.py` | Python 3 | Wall-clock execution timing and $\ge 20\%$ speedup validation | `--baseline-time`, `--base-cmd`, `--min-speedup-pct`, `--repeats` |
| `tests/test_cli.py` | Python 3 | CLI argument parsing and plane validation against `planes_list.txt` | `--bin`, `--module`, `--planes-list`, `--strict`, `--verbose` |
| `tests/run_e2e_tests.sh` | Bash | Master runner executing all 4 test tiers with colored summary table | `--tier <1\|2\|3\|4\|all>`, `--strict`, `--require-optimized`, `-v` |

---

## 3. Four-Tier Verification Architecture

The test suite is structured into four sequential tiers per `SCOPE.md`:

```
+--------------------------------------------------------------------------+
| Tier 1: Feature Coverage                                                 |
| - Verify MD5 checksum validator on baseline dataset                      |
| - Verify Darwin-aware peak RSS sampling harness                          |
| - Verify wall-clock speedup measurement calculation                      |
| - Verify CLI argument parser on compiled binaries                        |
+--------------------------------------------------------------------------+
                                     |
                                     v
+--------------------------------------------------------------------------+
| Tier 2: Boundary & Corner Cases                                          |
| - Out-of-bounds plane rejection (e.g. plane 999, plane 55, plane -1)     |
| - Snapshot mismatch rejection (e.g. snap 99 for plane 1, snap 70 plane 0) |
| - Malformed argument rejection (0 args, 1 arg, non-integer inputs)       |
| - Memory ceiling threshold breach enforcement (fails with exit code 3)   |
+--------------------------------------------------------------------------+
                                     |
                                     v
+--------------------------------------------------------------------------+
| Tier 3: Cross-Feature Combinations                                       |
| - Pairwise CLI invocation across multiple RAM ceilings (4GB, 8GB, 16GB)  |
| - Data contract verification: LC catalog schema (12 columns) matching   |
|   DF ingestion schema, DF flux output schema (14 columns)                |
+--------------------------------------------------------------------------+
                                     |
                                     v
+--------------------------------------------------------------------------+
| Tier 4: Real-World Application Scenarios                                 |
| - Test Planes validation (Rows 1, 2, 4: Snap 98, Planes 0, 1, 3)         |
| - Bit-exact output comparison against /output_baseline/                  |
| - Performance benchmark: >= 20% single-core wall-clock speedup           |
+--------------------------------------------------------------------------+
```

---

## 4. Authoritative Baseline Reference Data

### Validation Test Planes (Rows 1, 2, and 4)
Validation is conducted on Rows 1, 2, and 4 from `/Volumes/PMSAdrive/pmsa/storage/TNG/optimization/planes_list.txt`:

| Row in `planes_list.txt` | Display Plane (`Col 1`) | Redshift (`Col 2`) | Replica / Plane Index (`Col 5`) | Snapshot (`Col 6`) |
| :---: | :---: | :---: | :---: | :---: |
| **Row 1** | `1` | `0.0108551` | `0` | `98` |
| **Row 2** | `2` | `0.0175277` | `1` | `98` |
| **Row 4** | `4` | `0.0418893` | `3` | `98` |

### Authoritative MD5 Hash & Size Matrix
All files generated in `/Volumes/PMSAdrive/pmsa/storage/TNG/output_optimized/` must match these exact checksums:

| Module | Catalog File | Size (Bytes) | Authoritative MD5 Checksum |
|---|---|---|---|
| **LC** | `coords.lc.98_0.txt` | 1,066 | `79ac9efb68c8ce6e08b1c7c09dd887ab` |
| **LC** | `coords.lc.98_1.txt` | 459,433 | `b1fc04316bb7a955d4f5df47a90628f7` |
| **LC** | `coords.lc.98_3.txt` | 17,901,836 | `9f9ff464b433c58f4104881a0efaa748` |
| **DF** | `flux.df.98_0.txt` | 1,234 | `a9eb9b4aad5e6e65bc220b462005f2bd` |
| **DF** | `flux.df.98_1.txt` | 539,176 | `cb8cdb62e2bf14bcbd6ff4c813044d80` |
| **DF** | `flux.df.98_3.txt` | 21,870,357 | `acbbb175ac0052dec2808c583b4a0d7d` |

---

## 5. Platform Memory Mechanics (macOS Darwin)

### The Darwin RSS Byte Conversion Rule
On Linux, `resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss` is expressed in **kilobytes**.  
On **macOS (Darwin)**, `ru_maxrss` is expressed in **bytes**.

- **Incorrect Linux formula on macOS**:
  $$\text{RSS}_{\text{MB}} = \frac{\text{ru\_maxrss}}{1024} \quad (\text{Inflates memory by } 1024\times!)$$
- **Correct Darwin formula**:
  $$\text{RSS}_{\text{MB}} = \frac{\text{ru\_maxrss}}{1024 \times 1024}$$

`tests/monitor_rss.py` detects `sys.platform == 'darwin'` and dynamically applies the byte scaling divisor, while also performing live high-frequency polling via `ps -o rss=` (which reports in KB on both platforms).

---

## 6. CLI Interface Contracts & Exit Codes

Per `PROJECT.md`, the pipeline executables and verification harnesses conform to the following contract:

### CLI Syntax
```bash
./lc/executable_lc <snapshot> <plane_number> [memory_ceiling_gb]
./df/executable_df <snapshot> <plane_number> [memory_ceiling_gb]
```

### Standardized Exit Codes
| Exit Code | Meaning |
| :---: | :--- |
| `0` | **Success**: Processing completed successfully within memory limit. |
| `1` | **Invalid Arguments / Failed Plane Validation**: Wrong argument count, non-numeric arguments, plane index not in `planes_list.txt`, or snapshot mismatch. |
| `2` | **Missing Configuration or Input Data**: Parameter file or input particle catalog cannot be found. |
| `3` | **Memory Ceiling Exceeded**: Peak RSS exceeded the configured ceiling during execution. |

---

## 7. How to Run Verification Suites

### Run All Tiers (Master Test Runner)
```bash
bash tests/run_e2e_tests.sh
```

### Run Specific Test Tier
```bash
bash tests/run_e2e_tests.sh --tier 1
bash tests/run_e2e_tests.sh --tier 2
bash tests/run_e2e_tests.sh --tier 3
bash tests/run_e2e_tests.sh --tier 4
```

### Standalone Verification Recipes

#### 1. Bit-Exact MD5 Verification
```bash
# Verify baseline integrity:
python3 tests/verify_md5.py --baseline-only

# Verify optimized outputs against baseline:
python3 tests/verify_md5.py --module all --planes 0,1,3
```

#### 2. Peak RSS Memory Ceiling Enforcement
```bash
# Monitor LC execution under 4 GB ceiling:
python3 tests/monitor_rss.py --ceiling-gb 4.0 -- ./lc/executable_lc 98 0 4.0

# Monitor DF execution under 8 GB ceiling:
python3 tests/monitor_rss.py --ceiling-gb 8.0 -- ./df/executable_df 98 1 8.0
```

#### 3. Single-Core Wall-Clock Speedup Measurement
```bash
# Verify >= 20% speedup against recorded baseline time (e.g. 3.20s for LC plane 1):
python3 tests/benchmark_speedup.py --baseline-time 3.20 --min-speedup-pct 20.0 -- ./lc/executable_lc 98 1

# Direct live comparison between baseline and optimized executables:
python3 tests/benchmark_speedup.py --base-cmd "./executable_lc_base 98 1" --opt-cmd "./executable_lc_opt 98 1"
```

#### 4. CLI & Plane Validation Test Suite
```bash
# Test executable_df argument handling:
python3 tests/test_cli.py --bin ./df/executable_df

# Test executable_lc argument handling:
python3 tests/test_cli.py --bin ./lc/executable_lc
```
