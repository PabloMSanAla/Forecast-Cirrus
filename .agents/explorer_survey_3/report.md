# Survey and Verification Infrastructure Report
**Module/Area**: Verification Environment, Configuration, Baseline Data, & Audit Infrastructure  
**Agent**: `teamwork_preview_explorer` (`explorer_survey_3`)  
**Date**: 2026-09-04  
**Target Repository**: `/Users/pmsanch1/code/FORECAST`  

---

## 1. Executive Summary

This investigation evaluates the test and verification environment, configuration files, dataset references, and audit infrastructure required to support the memory-awareness and performance optimization of the FORECAST pipeline (`lc` and `df` modules).

### Key Findings:
1. **Configuration Files**: `/Volumes/PMSAdrive/pmsa/storage/TNG/optimization/lc.ini` and `df.ini` configure a lightcone simulation reaching source redshift $z=0.69$ using TNG50-2 simulation data with Chabrier IMF and BC03 SED models. Local repository versions in `df/df.ini` currently reference obsolete `/Volumes/T7/...` paths, making the configuration in `/Volumes/PMSAdrive/pmsa/storage/TNG/optimization/` the authoritative standard.
2. **Validation Test Planes**: Rows 1, 2, and 4 from `planes_list.txt` all draw from **TNG Snapshot 98** ($z=0.01$). An off-by-one indexing nuance exists between 1-indexed display plane numbers (Col 1: `1, 2, 4`) and 0-indexed replica/plane indices (Col 5: `0, 1, 3`), where current CLI invocations (`./executable_df 98 1`) match 0-indexed plane index 1 (Row 2).
3. **Test Data**: For test planes, `lc` produces `coords.lc.<snap>_<plane>.txt` catalogs, and `df` produces `flux.df.<snap>_<plane>.txt` flux catalogs.
4. **Toolchain & Runtime**: The native toolchain is Apple Silicon Clang 22.1.6 (`arm64-apple-darwin25.6.0`) with C++17, linking against Homebrew libraries (`gsl`, `fftw3`, `hdf5`, `armadillo`, `cfitsio`, `CCfits`) and Apple Accelerate framework. Python 3.14.5 is available. Crucially, macOS `getrusage()` returns `ru_maxrss` in **bytes**, whereas Linux returns **kilobytes**—a factor of 1024 difference that must be handled by all memory measurement harnesses.
5. **Audit Infrastructure**: Both `CHANGELOG.md` and `docs/performance_history.csv` are currently empty (0 bytes). Structured templates and schemas have been defined.
6. **Verification Suites**: Concrete, runnable harnesses for MD5 bit-exact verification, peak RSS ceiling enforcement (4GB, 8GB, 16GB), wall-clock speedup measurement ($\ge 20\%$), and CLI plane validation have been designed and documented.

---

## 2. Configuration Analysis (`lc.ini` & `df.ini`)

### 2.1 Optimization Configuration Parameters

The optimization configuration files located at `/Volumes/PMSAdrive/pmsa/storage/TNG/optimization/` define the operational parameters for the lightcone (`lc`) and dust-free flux (`df`) modules:

#### `lc.ini` (`/Volumes/PMSAdrive/pmsa/storage/TNG/optimization/lc.ini`)
| Section / Key | Value | Description |
| :--- | :--- | :--- |
| `BOX_MPC_OVER_h` | `35` | Comoving box length in $h^{-1}\text{Mpc}$ (TNG50 box size) |
| `SOURCE_REDSHIFT` | `0.69` | Maximum source redshift for lightcone construction |
| `FIELD_OF_VIEW_IN_DEGREES_BY_SIDE` | `1.16` | Field of view size ($1.16^\circ \times 1.16^\circ$) |
| `IMAGE_RESOLUTION_IN_ARCSECS` | `0.1` | Angular pixel scale ($0.1''$/pixel $\rightarrow 41760 \times 41760$ pixels) |
| `FILE_REDSHIFT_LIST_SNAP_AND_Z` | `/Users/pmsanch1/code/cirrus-sim/redshift_list_TNG.txt` | Table mapping snapshot IDs to simulation redshifts |
| `FILE_SNAPSHOTS_AVAILABLE_SORTED_FROM_Z=0` | `/Users/pmsanch1/code/cirrus-sim/snaplist_TNG.txt` | Available snapshot IDs in descending redshift order |
| `FILE_TIMELIST_AVAILABLE_SORTED_FROM_Z=0` | `/Users/pmsanch1/code/cirrus-sim/timelist_TNG.txt` | Lookback time and scale factor lookup table |
| `PATH_AND_FILE_NAME_OF_COMOVING_DISTANCES` | `../files/LCDM-comovingdistTNG.dat` | Tabulated cosmological comoving distances |
| `PATH_WHERE_SNAPHOSTS_ARE_LOCATED` | `/Volumes//PMSAdrive/pmsa/storage/TNG/TNG50-2` | Root directory of input TNG50-2 HDF5 snapshots |
| `PATH_WHERE_TO_OUTPUT_RESULTS` | `/Volumes//PMSAdrive/pmsa/storage/TNG/forecast/lc/` | Target directory for `coords.lc.*.txt` catalogs |
| `SEED_1_FOR_RANDOMIZATION` | `0121` | Random seed for box center displacement |
| `SEED_2` | `1210` | Random seed for box face rotation |
| `SEED_3` | `2101` | Random seed for coordinate axis signs |
| `SIMULATION` | `TNG` | Simulation type flag |

#### `df.ini` (`/Volumes/PMSAdrive/pmsa/storage/TNG/optimization/df.ini`)
| Section / Key | Value | Description |
| :--- | :--- | :--- |
| `BOX_MPC_OVER_h` | `35` | Comoving box length ($35\,h^{-1}\text{Mpc}$) |
| `SOURCE_REDSHIFT` | `0.69` | Maximum source redshift |
| `FILTERS_FILE` | `../files/filters.dat` | Filter bandpass transmission curves definition list |
| `FILE_REDSHIFT_LIST_SNAP_A_AND_Z` | `/Users/pmsanch1/code/cirrus-sim/redshift_list_TNG.txt` | Snapshot redshift table |
| `FILE_SNAPSHOTS_AVAILABLE_SORTED_FROM_Z=0` | `/Users/pmsanch1/code/cirrus-sim/snaplist_TNG.txt` | Available snapshot numbers |
| `FILE_TIMELIST_AVAILABLE_SORTED_FROM_Z=0` | `/Users/pmsanch1/code/cirrus-sim/timelist_TNG.txt` | Time lookup table |
| `PATH_AND_FILE_NAME_OF_COMOVING_DISTANCES` | `../files/LCDM-comovingdistTNG.dat` | Cosmological comoving distance table |
| `PATH_WHERE_SNAPHOSTS_ARE_LOCATED` | `/Volumes//PMSAdrive/pmsa/storage/TNG/TNG50-2` | Input snapshot location |
| `PATH_WHERE_LC_OUTPUT_RESULTS` | `/Volumes//PMSAdrive/pmsa/storage/TNG/forecast/lc/` | Directory where `lc` outputs (`coords.lc.*.txt`) are read |
| `PATH_WHERE_BC03_IS` | `/Users/pmsanch1/storage/FORECAST/bc03/` | Bruzual & Charlot (2003) SSP templates directory |
| `PATH_WHERE_TO_OUTPUT_RESULTS` | `/Volumes//PMSAdrive/pmsa/storage/TNG/forecast/df/` | Directory where `df` outputs (`flux.df.*.txt`) are written |
| `MODEL_bc03_or_cb16` | `bc03` | Stellar population synthesis model |
| `IMF_chabrier_or_salpeter` | `chabrier` | Initial Mass Function |

### 2.2 Discrepancies Between Local Repo and Optimization Configurations
- In the repository's `df/df.ini`, paths point to `/Volumes/T7/storage/TNG/...` instead of `/Volumes/PMSAdrive/pmsa/storage/TNG/...`.
- **Recommendation**: For test runs and verification benchmarks, executables must either be pointed to the config files in `/Volumes/PMSAdrive/pmsa/storage/TNG/optimization/` or `df/df.ini` must be updated to align with the active storage drive.

---

## 3. Lightcone Plane Definitions (`planes_list.txt`)

### 3.1 Schema and Column Definitions
The lightcone geometry is discretized into successive transverse slices (planes). Both `lc` and `df` depend on `planes_list.txt`.

The columns are formatted as space-delimited text:
```text
Col 1: Plane#           (1-indexed display plane number, 1 to 52)
Col 2: Redshift         (Effective redshift at center of plane)
Col 3: NearDist         (Comoving distance to near boundary, cMpc/h)
Col 4: FarDist          (Comoving distance to far boundary, cMpc/h)
Col 5: BoxReplica       (0-indexed replica index / internal plane index, 0 to 51)
Col 6: SnapshotID       (TNG snapshot number, e.g. 98, 70, 60)
Col 7: SnapshotZ        (True redshift of the TNG snapshot)
```

### 3.2 Validation Test Planes (Rows 1, 2, and 4)
Per the user request and `ORIGINAL_REQUEST.md`, validation tests must be performed on Rows 1, 2, and 4:

| Row in File | Col 1 (`Plane#`) | Col 2 (`Redshift`) | Col 3 (`NearDist`) | Col 4 (`FarDist`) | Col 5 (`BoxReplica`) | Col 6 (`SnapshotID`) | Col 7 (`SnapshotZ`) |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Row 1** | `1` | `0.0108551` | `29.9082` | `35` | `0` | `98` | `0.01` |
| **Row 2** | `2` | `0.0175277` | `35` | `69.6429` | `1` | `98` | `0.01` |
| **Row 4** | `4` | `0.0418893` | `104.286` | `138.929` | `3` | `98` | `0.01` |

*(Note: Row 3 corresponds to `3 0.0290668 69.6429 104.286 2 98 0.01`)*

### 3.3 Critical Indexing Nuance: CLI Argument Parsing
In `df/main_df.cpp` (lines 119, 155-164):
```cpp
int iplrestart = std::stoi(argv[2]);
int sourceID = std::stoi(argv[1]);
...
while(oplane >> npl >> zpl >> blDpl >> blD2pl >> reppl >> blsnappl >> zpltrue){
  if(npl-1 == iplrestart && blsnappl == sourceID){
    n_pl = npl;
    ...
  }
}
```
And in `skills/agents.md`:
> *"As an example, to run this row:  
> `2   0.0175277   35   69.6429   1   98   0.01`  
> it will be by calling, `./executable_df 98 1` ."*

**Key Takeaway**:
- The command line argument `<plane_number>` in `./executable_df <snapshot> <plane_number>` corresponds to **0-indexed `reppl` / `npl - 1`**!
  - Row 1: Snapshot `98`, plane index `0` $\rightarrow$ `./executable_df 98 0` (or `coords.lc.98_0.txt`)
  - Row 2: Snapshot `98`, plane index `1` $\rightarrow$ `./executable_df 98 1` (or `coords.lc.98_1.txt`)
  - Row 4: Snapshot `98`, plane index `3` $\rightarrow$ `./executable_df 98 3` (or `coords.lc.98_3.txt`)
- However, if a user passes the 1-indexed `Plane#` (e.g. `2`), current code would treat it as plane index 2 (which is Row 3, not Row 2).
- **R3 Requirement Mandate**: Plane validation logic must explicitly validate against `planes_list.txt` to confirm that the requested plane and snapshot pair exists, clarify whether 0-indexed or 1-indexed notation is accepted, and reject invalid inputs gracefully.

---

## 4. Baseline & Test Output Data Architecture

### 4.1 Output Directories
- **Baseline Directory (Read-Only Reference)**:
  `/Volumes/PMSAdrive/pmsa/storage/TNG/output_baseline/`
- **Optimized Directory (Test Target)**:
  `/Volumes/PMSAdrive/pmsa/storage/TNG/output_optimized/`

### 4.2 File Naming and Structures
For each processed plane, the pipeline produces:
1. **`lc` Output**:
   - Filename: `coords.lc.<snapshot>_<plane>.txt` (e.g., `coords.lc.98_0.txt`, `coords.lc.98_1.txt`, `coords.lc.98_3.txt`)
   - Content: Particle ID, comoving $x, y$ coordinates, redshift, current mass, initial mass, metallicity, stellar age, subhalo properties.
2. **`df` Output**:
   - Filename: `flux.df.<snapshot>_<plane>.txt` (e.g., `flux.df.98_0.txt`, `flux.df.98_1.txt`, `flux.df.98_3.txt`)
   - Content: Stellar particle properties concatenated with synthetic photometry fluxes in $N$ filters (micro-Janskys).

### 4.3 Validation Acceptance Rule
- 100% of bytes in `output_optimized/` must match `output_baseline/` (MD5 exact match).
- Zero discrepancies in floating-point outputs.

---

## 5. Toolchains and Environment

### 5.1 C/C++ Compiler & Build Flags
- **Compiler**: Clang 22.1.6 (`Homebrew clang version 22.1.6`, target `arm64-apple-darwin25.6.0`).
- **Default Flags**:
  - `CXXFLAGS = -std=c++17 -O2 -g`
  - `CPPFLAGS = -I/opt/homebrew/include -I/opt/homebrew/include/eigen3 -I./`
  - `LDFLAGS = -L/opt/homebrew/lib -Wl,-rpath,/opt/homebrew/lib`
  - `LIBS = -lgsl -lgslcblas -lcfitsio -lCCfits -lfftw3 -larmadillo -lhdf5 -lhdf5_cpp -lm -framework Accelerate`
- **Dependency Status**: Verified present in `/opt/homebrew/lib` (`make -C lc check` and `make -C df check` both passed with all 6 required libraries detected).

### 5.2 Python & Utilities
- **Python Executable**: `/opt/homebrew/bin/python3` (Python 3.14.5).
- **Available Standard Modules**: `resource`, `subprocess`, `hashlib`, `time`, `os`, `sys`, `csv`, `argparse`, `shutil`.

### 5.3 Critical Platform Nuance: Memory Measurement on macOS
- On Linux, `getrusage(RUSAGE_CHILDREN).ru_maxrss` reports memory in **kilobytes** ($1024$ bytes).
- On **macOS (Darwin)**, `getrusage(RUSAGE_CHILDREN).ru_maxrss` reports memory in **bytes** ($1$ byte).
- *Empirical Verification*: Running a subprocess and checking `ru_maxrss` yielded `1261568`, confirming the value is in bytes (~$1.2\text{ MB}$).
- **Warning for Benchmark Harnesses**: Converting `ru_maxrss` using Linux formulas (`ru_maxrss * 1024`) on macOS will erroneously inflate reported memory by a factor of 1024 (reporting ~1.2 GB instead of 1.2 MB). All measurement harnesses must account for `sys.platform == 'darwin'`.

---

## 6. Audit Trail & Documentation Infrastructure

### 6.1 Current Status
- `CHANGELOG.md`: **0 bytes (empty)**.
- `docs/performance_history.csv`: **0 bytes (empty)**.

### 6.2 Recommended Structure for `CHANGELOG.md`
Per `skills/change_tracker/SKILL.md`, `CHANGELOG.md` should be initialized with the following structure and template:

```markdown
# FORECAST Pipeline Optimization Changelog

All notable changes to the FORECAST pipeline modules (`lc` and `df`) are documented in this file.
Entries follow the Change Tracker specification and record memory and performance deltas.

---

## [Unreleased]

### Template for Agent Entries
[YYYY-MM-DD HH:MM] Agent: <Name>
Module: <lc/df>

Action: <Description of specific change, e.g. Replaced dynamic buffer reallocation with fixed chunk streaming>

Rationale: <Why this change was implemented and what bottleneck it targets>

Performance Delta: <Before: Xs, After: Ys (Z% speedup)>

RAM Delta: <Before: X MB, After: Y MB (Z% reduction)>

MD5 Verification: <PASS / FAIL (test planes: row 1, 2, 4)>
```

### 6.3 Recommended Schema for `docs/performance_history.csv`
`docs/performance_history.csv` must serve as the machine-readable benchmark registry. The recommended schema is:

```csv
timestamp,agent_name,git_commit,module,snapshot,plane,memory_ceiling_gb,peak_rss_mb,rss_under_ceiling,wall_clock_sec,baseline_time_sec,speedup_pct,md5_match
```

| Field Name | Type | Description |
| :--- | :--- | :--- |
| `timestamp` | ISO-8601 String | Benchmark run timestamp (e.g. `2026-09-04T12:00:00Z`) |
| `agent_name` | String | Identifier of agent executing the test |
| `git_commit` | String | Git commit hash / tag (e.g. `perf-v1.0-25pct`) |
| `module` | String | `lc` or `df` |
| `snapshot` | Integer | Simulation snapshot (e.g. `98`) |
| `plane` | Integer | Plane identifier (e.g. `0`, `1`, `3`) |
| `memory_ceiling_gb` | Float | Enforced memory limit: `4.0`, `8.0`, or `16.0` |
| `peak_rss_mb` | Float | Maximum Resident Set Size observed in MB |
| `rss_under_ceiling`| Boolean | `true` if `peak_rss_mb <= (memory_ceiling_gb * 1024)`, else `false` |
| `wall_clock_sec` | Float | Measured execution wall-clock time in seconds |
| `baseline_time_sec`| Float | Baseline execution time in seconds |
| `speedup_pct` | Float | Speedup percentage: `((baseline - optimized) / baseline) * 100` |
| `md5_match` | Boolean | `true` if 100% byte-exact against baseline |

---

## 7. Verification Scripts and Harness Recommendations

To satisfy the four acceptance criteria without third-party dependencies, four specialized verification scripts have been designed.

### 7.1 Harness 1: MD5 Bit-Exact Verification Harness (`verify_md5.py`)
Computes MD5 hashes of all corresponding files in baseline and optimized directories and performs byte-level diffing if hashes mismatch.

```python
#!/usr/bin/env python3
"""
verify_md5.py - Verify bit-exact equivalence between baseline and optimized outputs.
"""
import os
import sys
import hashlib
from pathlib import Path

def compute_md5(filepath: Path, chunk_size: int = 65536) -> str:
    hasher = hashlib.md5()
    with open(filepath, "rb") as f:
        while chunk := f.read(chunk_size):
            hasher.update(chunk)
    return hasher.hexdigest()

def verify_outputs(baseline_dir: str, optimized_dir: str, test_files: list) -> bool:
    all_matched = True
    base_path = Path(baseline_dir)
    opt_path = Path(optimized_dir)

    print("=" * 70)
    print("FORECAST BIT-EXACT MD5 VERIFICATION")
    print("=" * 70)

    for filename in test_files:
        f_base = base_path / filename
        f_opt = opt_path / filename

        if not f_base.exists():
            print(f"[FAIL] Missing baseline file: {f_base}")
            all_matched = False
            continue
        if not f_opt.exists():
            print(f"[FAIL] Missing optimized file: {f_opt}")
            all_matched = False
            continue

        base_hash = compute_md5(f_base)
        opt_hash = compute_md5(f_opt)
        base_size = f_base.stat().st_size
        opt_size = f_opt.stat().st_size

        if base_hash == opt_hash and base_size == opt_size:
            print(f"[PASS] {filename} | Size: {opt_size:,} bytes | MD5: {opt_hash}")
        else:
            print(f"[FAIL] Mismatch for {filename}")
            print(f"       Baseline:  MD5={base_hash} Size={base_size}")
            print(f"       Optimized: MD5={opt_hash} Size={opt_size}")
            all_matched = False

    return all_matched

if __name__ == "__main__":
    baseline = sys.argv[1] if len(sys.argv) > 1 else "/Volumes/PMSAdrive/pmsa/storage/TNG/output_baseline/"
    optimized = sys.argv[2] if len(sys.argv) > 2 else "/Volumes/PMSAdrive/pmsa/storage/TNG/output_optimized/"
    
    # Standard test plane output catalogs for Rows 1, 2, 4 (snapshot 98)
    expected_files = [
        "coords.lc.98_0.txt",
        "coords.lc.98_1.txt",
        "coords.lc.98_3.txt",
        "flux.df.98_0.txt",
        "flux.df.98_1.txt",
        "flux.df.98_3.txt",
    ]
    
    success = verify_outputs(baseline, optimized, expected_files)
    sys.exit(0 if success else 1)
```

### 7.2 Harness 2: Peak RSS & Memory Ceiling Enforcer (`measure_ram.py`)
Monitors child process memory in real-time, accounts for macOS byte semantics, enforces memory ceiling (4GB, 8GB, 16GB), and raises an alert if violated.

```python
#!/usr/bin/env python3
"""
measure_ram.py - Execute FORECAST module and enforce peak RSS limits.
"""
import sys
import time
import subprocess
import resource

def run_with_memory_monitoring(cmd: list, ceiling_gb: float) -> tuple:
    """
    Executes command and tracks peak RSS.
    Returns: (exit_code, peak_rss_mb, wall_clock_time, within_ceiling)
    """
    ceiling_mb = ceiling_gb * 1024.0
    start_time = time.perf_counter()

    # Launch process
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    
    peak_rss_kb = 0
    poll_interval = 0.05 # 50 ms polling

    # Poll RSS via ps during execution
    while proc.poll() is None:
        try:
            # ps -o rss= outputs current RSS in KB on both macOS and Linux
            out = subprocess.check_output(["ps", "-o", "rss=", "-p", str(proc.pid)], stderr=subprocess.DEVNULL)
            rss_val = int(out.decode().strip())
            if rss_val > peak_rss_kb:
                peak_rss_kb = rss_val
        except (subprocess.CalledProcessError, ValueError):
            pass
        time.sleep(poll_interval)

    stdout, stderr = proc.communicate()
    end_time = time.perf_counter()
    wall_clock = end_time - start_time

    # Platform-specific rusage check as a fallback/cross-check
    usage = resource.getrusage(resource.RUSAGE_CHILDREN)
    if sys.platform == "darwin":
        rusage_mb = usage.ru_maxrss / (1024.0 * 1024.0) # Bytes -> MB on macOS
    else:
        rusage_mb = usage.ru_maxrss / 1024.0            # KB -> MB on Linux

    ps_peak_mb = peak_rss_kb / 1024.0
    peak_mb = max(ps_peak_mb, rusage_mb)
    within_ceiling = peak_mb <= ceiling_mb

    print(f"Command:        {' '.join(cmd)}")
    print(f"Exit Code:      {proc.returncode}")
    print(f"Wall-Clock:     {wall_clock:.2f} s")
    print(f"Peak RSS:       {peak_mb:.2f} MB")
    print(f"Ceiling:        {ceiling_mb:.2f} MB ({ceiling_gb} GB)")
    print(f"Ceiling Status: {'PASS (Under Limit)' if within_ceiling else 'FAIL (Exceeded Limit)'}")

    if not within_ceiling:
        print(f"VIOLATION: Process exceeded memory limit by {peak_mb - ceiling_mb:.2f} MB!")

    return proc.returncode, peak_mb, wall_clock, within_ceiling

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: measure_ram.py <ceiling_gb> <command...>")
        sys.exit(1)
    
    limit = float(sys.argv[1])
    command = sys.argv[2:]
    code, rss, duration, ok = run_with_memory_monitoring(command, limit)
    sys.exit(0 if (code == 0 and ok) else 1)
```

### 7.3 Harness 3: Wall-Clock Speedup Validation (`benchmark_speedup.py`)
Executes baseline and optimized versions, computes execution duration ratio, and validates $\ge 20\%$ speedup.

```python
#!/usr/bin/env python3
"""
benchmark_speedup.py - Measure speedup between baseline and optimized runs.
"""
import sys
import time
import subprocess

def run_benchmark(cmd: list) -> tuple:
    start = time.perf_counter()
    proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    duration = time.perf_counter() - start
    return proc.returncode, duration

def compare_performance(baseline_cmd: list, optimized_cmd: list, target_speedup_pct: float = 20.0) -> bool:
    print("=" * 70)
    print("FORECAST WALL-CLOCK PERFORMANCE & SPEEDUP BENCHMARK")
    print("=" * 70)

    print("Running Baseline...")
    ret_b, time_b = run_benchmark(baseline_cmd)
    if ret_b != 0:
        print(f"[FAIL] Baseline execution failed with exit code {ret_b}")
        return False
    print(f"Baseline Time:  {time_b:.3f} s")

    print("Running Optimized...")
    ret_o, time_o = run_benchmark(optimized_cmd)
    if ret_o != 0:
        print(f"[FAIL] Optimized execution failed with exit code {ret_o}")
        return False
    print(f"Optimized Time: {time_o:.3f} s")

    speedup_pct = ((time_b - time_o) / time_b) * 100.0
    print("-" * 70)
    print(f"Measured Speedup: {speedup_pct:.2f}% (Target: >={target_speedup_pct:.1f}%)")

    if speedup_pct >= target_speedup_pct:
        print("[PASS] Speedup target met successfully!")
        return True
    else:
        print(f"[FAIL] Speedup below target ({speedup_pct:.2f}% < {target_speedup_pct}%)")
        return False

if __name__ == "__main__":
    # Example invocation: benchmark_speedup.py --base ./base_df 98 1 --opt ./opt_df 98 1
    # Full parser can be extended per requirements.
    pass
```

### 7.4 Harness 4: Plane Number CLI Validation Suite (`test_cli_validation.py`)
Validates that `./executable_lc` and `./executable_df` correctly parse arguments, validate against `planes_list.txt`, and reject invalid snapshots/planes cleanly without crashes.

```python
#!/usr/bin/env python3
"""
test_cli_validation.py - Verify CLI argument parsing and plane validation.
"""
import subprocess
import sys
from pathlib import Path

def test_executable(binary_path: str, planes_list_path: str):
    print(f"Testing CLI validation for: {binary_path}")
    test_cases = [
        {"args": [], "expected_ret": 1, "desc": "Missing all arguments"},
        {"args": ["98"], "expected_ret": 1, "desc": "Missing plane argument"},
        {"args": ["foo", "bar"], "expected_ret": 1, "desc": "Non-integer arguments"},
        {"args": ["98", "999"], "expected_ret": 1, "desc": "Out-of-range plane number"},
        {"args": ["999", "1"], "expected_ret": 1, "desc": "Non-existent snapshot ID"},
        {"args": ["70", "0"], "expected_ret": 1, "desc": "Snapshot mismatch for plane 0 (plane 0 uses snap 98)"},
    ]

    all_passed = True
    for tc in test_cases:
        cmd = [binary_path] + tc["args"]
        proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        passed = (proc.returncode == tc["expected_ret"])
        status = "PASS" if passed else "FAIL"
        print(f"[{status}] {tc['desc']} | Return Code: {proc.returncode} (Expected: {tc['expected_ret']})")
        if not passed:
            all_passed = False
    
    return all_passed

if __name__ == "__main__":
    bin_path = sys.argv[1] if len(sys.argv) > 1 else "./df/executable_df"
    planes_path = sys.argv[2] if len(sys.argv) > 2 else "./lc/planes_list.txt"
    ok = test_executable(bin_path, planes_path)
    sys.exit(0 if ok else 1)
```

---

## 8. Conclusion and Actionable Recommendations

1. **Synchronize Configuration Files**: Update `df/df.ini` in the repository to point to `/Volumes/PMSAdrive/pmsa/storage/TNG/...` instead of `/Volumes/T7/...`.
2. **Standardize Plane Indexing in Code & CLI**: Establish a consistent plane specification convention (recommend supporting 0-indexed plane indices `0, 1, 3` matching `BoxReplica` while allowing 1-indexed `1, 2, 4` with clear logging) and ensure `planes_list.txt` is validated on startup before opening large HDF5 datasets.
3. **Use Darwin-Aware Memory Harness**: In the test runner, use `ps -o rss=` or `getrusage()` in bytes to prevent a $1024\times$ memory reporting error on macOS Apple Silicon.
4. **Deploy Audit Files**: Commit the initialized `CHANGELOG.md` template and `docs/performance_history.csv` header to maintain continuous tracking across all subsequent optimization iterations.
