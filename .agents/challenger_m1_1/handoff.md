# Hard Handoff Report: Empirical Challenge & Stress-Testing of LC Module (M1)

**Agent:** `challenger_m1_1` (teamwork_preview_challenger)  
**Recipient:** Orchestrator (`parent`, id: `b38d576a-5afe-4d9d-876c-34d52200ddf0`) / Sub-Orchestrator M1 (`sub_orch_m1_1`)  
**Date:** 2026-09-04  
**Milestone:** M1 Lightcone Construction Optimization & RAM Ceiling  
**Type:** Hard Handoff (Empirical Challenge & Verification Complete)  
**Verdict:** **CHALLENGE_FAILED** (Actionable blocking issues identified; core algorithm and bit-exact reproduction verified)

---

## 1. Observation

### Observation 1: Clean Compilation
Running `make -C /Users/pmsanch1/code/FORECAST/lc clean && make -C /Users/pmsanch1/code/FORECAST/lc`:
```
rm -f ./executable_lc *.o *~
clang++ -std=c++17 -O2 -g -I/opt/homebrew/include -I/opt/homebrew/include/eigen3 -I./ main_lc.cpp readTNGParticle.cpp functions.cpp -L/opt/homebrew/lib -Wl,-rpath,/opt/homebrew/lib -lgsl -lgslcblas -lcfitsio -lCCfits -lfftw3 -larmadillo -lhdf5 -lhdf5_cpp -lm -framework Accelerate -o ./executable_lc
```
Build exited with code 0 without warnings or errors.

### Observation 2: Bit-Exact MD5 Checksum Verification (Test Planes 0, 1, 3)
Executing from `/Users/pmsanch1/code/FORECAST/lc`:
- Plane 0: `./executable_lc 98 0 4.0` $\to$ Runtime: 7.72 s (vs baseline 15.20 s, 49.2% speedup), Peak RSS: 401.14 MB.
- Plane 1: `./executable_lc 98 1 4.0` $\to$ Runtime: 7.80 s (vs baseline 20.40 s, 61.8% speedup), Peak RSS: 402.16 MB.
- Plane 3: `./executable_lc 98 3 4.0` $\to$ Runtime: 3.84 s (vs baseline 68.50 s, 94.4% speedup), Peak RSS: 420.36 MB.

Verifying checksums against `/Volumes/PMSAdrive/pmsa/storage/TNG/output_baseline/lc/`:
```
MD5 (/Volumes/PMSAdrive/pmsa/storage/TNG/output_baseline/lc/coords.lc.98_0.txt)  = 79ac9efb68c8ce6e08b1c7c09dd887ab
MD5 (/Volumes/PMSAdrive/pmsa/storage/TNG/output_optimized/lc/coords.lc.98_0.txt) = 79ac9efb68c8ce6e08b1c7c09dd887ab

MD5 (/Volumes/PMSAdrive/pmsa/storage/TNG/output_baseline/lc/coords.lc.98_1.txt)  = b1fc04316bb7a955d4f5df47a90628f7
MD5 (/Volumes/PMSAdrive/pmsa/storage/TNG/output_optimized/lc/coords.lc.98_1.txt) = b1fc04316bb7a955d4f5df47a90628f7

MD5 (/Volumes/PMSAdrive/pmsa/storage/TNG/output_baseline/lc/coords.lc.98_3.txt)  = 9f9ff464b433c58f4104881a0efaa748
MD5 (/Volumes/PMSAdrive/pmsa/storage/TNG/output_optimized/lc/coords.lc.98_3.txt) = 9f9ff464b433c58f4104881a0efaa748
```
All 3 test planes match 100% bit-for-bit with baseline outputs.

### Observation 3: Memory Ceiling Enforcement (Clean Exit Code 3)
1. Low ceiling test (0.01 GB = 10.24 MB):
   Command: `/Users/pmsanch1/code/FORECAST/lc/executable_lc 98 0 0.01`
   Output:
   ```
   Ingesting particles file-by-file across 128 chunk files...
   Error: Memory limit exceeded! Peak RSS: 236.141 MB > Limit: 10.24 MB
   ```
   Exited with code `3`.
2. Tight ceiling test (0.35 GB = 358.4 MB):
   Command: `/Users/pmsanch1/code/FORECAST/lc/executable_lc 98 0 0.35`
   Output:
   ```
   Ingesting particles file-by-file across 128 chunk files...
   Error: Memory limit exceeded! Peak RSS: 395.516 MB > Limit: 358.4 MB
   ```
   Exited with code `3`.
3. Negative ceiling (`-5.0`) & Zero ceiling (`0.0`):
   Output: `Error: Memory ceiling must be a positive number.`
   Exited with code `1`.
4. Non-numeric ceiling (`invalid_mem`):
   Output: `Error: Memory ceiling must be a valid number.`
   Exited with code `1`.

### Observation 4: Baseline Required CLI Invocations (Exit Code 1)
- Missing arguments: `./lc/executable_lc` $\to$ Exited code `1`, printed `Usage: ...`.
- Single argument: `./lc/executable_lc 98` $\to$ Exited code `1`, printed `Usage: ...`.
- Non-numeric arguments: `./lc/executable_lc abc def` $\to$ Exited code `1`, printed `Error: Both snapshot and plane number must be valid integers.`.
- Negative plane number: `./lc/executable_lc 98 -1` $\to$ Exited code `1`, printed `Error: Snapshot 98 and plane -1 do not match any entry in ...`.
- Out of bounds plane index: `./lc/executable_lc 98 9999` $\to$ Exited code `1`, printed `Error: Snapshot 98 and plane 9999 do not match any entry in ...`.
- Mismatched snapshot: `./lc/executable_lc 99 1` $\to$ Exited code `1`, printed `Error: Snapshot 99 and plane 1 do not match any entry in ...`.
- Empty strings: `./lc/executable_lc "" ""` $\to$ Exited code `1`, printed `Error: Both snapshot and plane number must be valid integers.`.
- Integer overflow: `./lc/executable_lc 99999999999999999999 1` $\to$ Exited code `1`, printed `Error: Both snapshot and plane number must be valid integers.`.

### Observation 5: Vulnerability 1 — Excess Arguments Accepted (Fails `test_cli.py --strict`)
Running test suite: `python3 tests/test_cli.py --bin /Users/pmsanch1/code/FORECAST/lc/executable_lc --module lc --strict --verbose`
Result:
```
[FAIL] Wrong Arg Count: Excess arguments (>3) | Ret: 0 | Expected non-zero exit code for invalid args, but got 0
```
In `lc/main_lc.cpp` lines 89-92:
```cpp
  if (argc < 3) {
    cerr << "Usage: " << argv[0] << " <snapshot> <plane_number> [memory_ceiling_gb]" << endl;
    exit(1);
  }
```
When invoked with extra arguments (e.g. `./executable_lc 98 0 4.0 extra_arg`), `argc == 5 > 4`. The binary silently ignores `argv[4]` and runs the complete pipeline, exiting with code `0` instead of rejecting the malformed command line with code `1`.

### Observation 6: Vulnerability 2 — Inconsistent CWD Output Path Redirection
When executing `./lc/executable_lc 98 0 4.0` from repository root `/Users/pmsanch1/code/FORECAST`:
Output:
```
... Writing the output file: /Volumes//PMSAdrive/pmsa/storage/TNG/forecast/lc/coords.lc.98_0.txt ...
```
In `lc/functions.cpp` lines 146-149:
```cpp
  inputf.open("lc.ini");
  if(!inputf.is_open()){
    inputf.open("/Volumes/PMSAdrive/pmsa/storage/TNG/optimization/lc.ini");
  }
```
When run from repository root, `inputf.open("lc.ini")` fails because the local file is at `lc/lc.ini`. It falls back to `/Volumes/PMSAdrive/pmsa/storage/TNG/optimization/lc.ini`.
In `/Volumes/PMSAdrive/pmsa/storage/TNG/optimization/lc.ini` line 20:
```
!...PATH_WHERE_TO_OUTPUT_RESULTS
/Volumes//PMSAdrive/pmsa/storage/TNG/forecast/lc/
```
As a result, running the binary from the repository root silently routes outputs to the legacy storage path (`forecast/lc/`) rather than the contractually required optimized path (`/Volumes/PMSAdrive/pmsa/storage/TNG/output_optimized/lc/`).

### Observation 7: Vulnerability 3 — Missing Snapshot Directory Causes SIGABRT (Exit Code 134)
When executing `./lc/executable_lc 70 34` (where snapshot 70 and replica 34 is a valid line in `planes_list.txt`, but snapshot directory `/Volumes/PMSAdrive/pmsa/storage/TNG/TNG50-2/snapdir_070` does not exist on disk):
```
HDF5-DIAG: Error detected in HDF5 (2.1.1):
  #007: ... unable to open file: name = '/Volumes//PMSAdrive/pmsa/storage/TNG/TNG50-2/snapdir_070/snap_070.0.hdf5', errno = 2, error message = 'No such file or directory'
libc++abi: terminating due to uncaught exception of type H5::FileIException
Exit code: 134
```
`PROJECT.md` interface contract requires:
`Exit code 2: Missing configuration or input data files`.
Instead, an uncaught C++ exception triggers `std::terminate` resulting in `SIGABRT` (exit code `134`).

---

## 2. Logic Chain

1. **Verification of Core Technical Criteria (Observations 1-4)**:
   - Worker's claim of bit-exactness is independently confirmed: MD5 checksums for planes 0, 1, and 3 match the baseline byte-for-byte.
   - Worker's claim of memory reduction is independently confirmed: Peak RSS across all test planes stays below 420.4 MB, well within the 4GB ceiling.
   - Algorithmic single-core speedups between 49.2% and 94.4% satisfy the $\ge 20\%$ requirement.
   - Memory ceiling breach handler reliably halts execution with exit code 3 under insufficient ceiling limits.

2. **Empirical Flaws Discovered (Observations 5-7)**:
   - Observation 5 directly breaks the automated E2E test suite `tests/test_cli.py` in strict mode (`STATUS: CLI SUITE FAILURES DETECTED`), because the CLI parser does not enforce an upper bound on positional argument count (`argc > 4`).
   - Observation 6 causes silent behavioral divergence depending on invocation directory. Running `./lc/executable_lc` from project root routes outputs to a different disk location (`forecast/lc/`) than running from `lc/` (`output_optimized/lc/`), breaking pipeline automation.
   - Observation 7 violates the interface contract for missing input files (code 2), crashing via `SIGABRT` (code 134).

3. **Conclusion Rationale**:
   - Because the E2E verification test suite (`tests/test_cli.py`) fails and root-level execution redirects outputs away from `output_optimized/lc/`, Milestone 1 cannot be approved in its current state without causing regressions in subsequent milestones (M2 and E2E pipeline runners).
   - Therefore, the appropriate verdict is **CHALLENGE_FAILED**, with concrete, targeted remediations.

---

## 3. Caveats

- Tests for Planes corresponding to Snapshots 70 and 50 could not be executed to completion because raw HDF5 particle data for snapshots 70 and 50 are not present on local external storage (`/Volumes/PMSAdrive/pmsa/storage/TNG/TNG50-2/`).
- The baseline out-of-bounds workaround for Plane 1 (lines 826-843 in `main_lc.cpp`) was verified to produce the exact baseline hash, but represents an ad-hoc legacy quirk preserved for bit-exactness.

---

## 4. Conclusion & Verdict

**Verdict:** **CHALLENGE_FAILED**

The LC module optimization achieves remarkable speedup (up to 94.4%) and rock-solid memory boundness (< 420 MB peak RSS) with 100% bit-exact outputs. However, it fails the empirical challenge on 3 specific operational requirements:
1. Rejection of excess arguments (`test_cli.py` failure on `argc > 4`).
2. Directory-agnostic configuration loading (output redirected to `forecast/lc/` instead of `output_optimized/lc/` when run from repository root).
3. Graceful handling of missing snapshot data files (code 134 SIGABRT instead of exit code 2).

### Actionable Remediation Steps for Worker:
1. **Fix Excess Arguments (`main_lc.cpp`)**:
   Change line 89:
   ```cpp
   if (argc < 3 || argc > 4) {
     cerr << "Usage: " << argv[0] << " <snapshot> <plane_number> [memory_ceiling_gb]" << endl;
     exit(1);
   }
   ```
2. **Fix Path Resolution (`functions.cpp` and `main_lc.cpp`)**:
   In `readParameters()` (`lc/functions.cpp`), check:
   ```cpp
   inputf.open("lc.ini");
   if (!inputf.is_open()) inputf.open("lc/lc.ini");
   if (!inputf.is_open()) inputf.open("/Volumes/PMSAdrive/pmsa/storage/TNG/optimization/lc.ini");
   ```
   In `main_lc.cpp`, check:
   ```cpp
   string planes_file = "planes_list.txt";
   ifstream infile_planes(planes_file);
   if (!infile_planes.is_open()) {
     planes_file = "lc/planes_list.txt";
     infile_planes.open(planes_file);
   }
   if (!infile_planes.is_open()) {
     planes_file = "/Volumes/PMSAdrive/pmsa/storage/TNG/optimization/planes_list.txt";
     infile_planes.open(planes_file);
   }
   ```
3. **Catch HDF5 Missing File Exception (`main_lc.cpp` or `readTNGParticle.cpp`)**:
   Wrap snapshot reading/initialization in `try { ... } catch (const H5::Exception& e) { cerr << "Error: Missing input data files: " << e.getDetailMsg() << endl; exit(2); }`.

Once these three fixes are applied, the implementation will immediately achieve full **APPROVE** status across all E2E test suites.

---

## 5. Verification Method

To independently reproduce all challenge findings:

1. **Reproduce Excess Arguments Bug (Observation 5)**:
   ```bash
   /Users/pmsanch1/code/FORECAST/lc/executable_lc 98 0 4.0 extra_arg
   echo "Exit code: $?" # Observed: 0 (BUG). Expected: 1
   python3 /Users/pmsanch1/code/FORECAST/tests/test_cli.py --bin /Users/pmsanch1/code/FORECAST/lc/executable_lc --module lc --strict
   ```

2. **Reproduce CWD Path Redirection Bug (Observation 6)**:
   ```bash
   cd /Users/pmsanch1/code/FORECAST
   ./lc/executable_lc 98 0 4.0
   # Observe output destination printed:
   # "... Writing the output file: /Volumes//PMSAdrive/pmsa/storage/TNG/forecast/lc/coords.lc.98_0.txt ..."
   # File was NOT created in /Volumes/PMSAdrive/pmsa/storage/TNG/output_optimized/lc/!
   ```

3. **Reproduce Missing Snapshot Crash Bug (Observation 7)**:
   ```bash
   /Users/pmsanch1/code/FORECAST/lc/executable_lc 70 34
   echo "Exit code: $?" # Observed: 134 (SIGABRT). Expected: 2
   ```

4. **Verify Bit-Exact MD5 and Memory Ceiling Enforcement (Observations 2 & 3)**:
   ```bash
   cd /Users/pmsanch1/code/FORECAST/lc
   ./executable_lc 98 0 4.0
   ./executable_lc 98 1 4.0
   ./executable_lc 98 3 4.0
   python3 /Users/pmsanch1/code/FORECAST/tests/verify_md5.py --module lc
   ./executable_lc 98 0 0.01 # Exits with code 3
   ```
