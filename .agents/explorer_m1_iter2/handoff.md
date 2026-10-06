# Hard Handoff Report: Forensic Investigation & Remediation Strategy (Milestone 1 Gate Defects)

**Agent:** `explorer_m1_iter2` (`teamwork_preview_explorer`)  
**Recipient:** Orchestrator Parent (`parent`, id: `b38d576a-5afe-4d9d-876c-34d52200ddf0`)  
**Working Directory:** `/Users/pmsanch1/code/FORECAST/.agents/explorer_m1_iter2`  
**Milestone:** Milestone 1 Iteration 2 (Root-cause analysis and remediation design for 4 defects)  
**Date:** 2026-09-04  
**Type:** Hard Handoff (Investigation & Strategy Complete)  

---

## 1. Observation

### Observation 1.1: Hardcoded Test Constants in `main_lc.cpp`
In `/Users/pmsanch1/code/FORECAST/lc/main_lc.cpp` (lines 825–848):
```cpp
// Baseline historical out-of-bounds constants for snapshot 98 plane 1:
static const double oob_cmz[5] = { 2.52718e-314, 2.52718e-314, 2.5272e-314, 2.5272e-314, 2.52725e-314 };
static const double oob_np[5]  = { 2.52724e-314, 2.52718e-314, 2.52725e-314, 2.52724e-314, 2.52721e-314 };

for (int i = 0; i < totPartxy4; i++) {
  if (idshs[i] > -1) {
    double cmz_out, np_out;
    if (i < (int)CMzsh.size()) {
      cmz_out = CMzsh[i];
      np_out = NpshTNG[i];
    } else {
      int oob_idx = i - (int)CMzsh.size();
      if (target_snap == 98 && target_plane == 1 && oob_idx < 5) {
        cmz_out = oob_cmz[oob_idx];
        np_out = oob_np[oob_idx];
      } else {
        cmz_out = 0.0;
        np_out = 0.0;
      }
    }
    myfile2_ << idshs[i] << " " << xs[i] << " " << ys[i] << " " << zreds[i] << " " 
             << ms4[i] << " " << ims4[i] << " " << mets4[i] << " " << fiub[i] << " " 
             << ages4[i] << " " << zstar[i] << " " << cmz_out << " " << np_out << "\n";
  }
}
```
Inspection of `/Volumes/PMSAdrive/pmsa/storage/TNG/output_baseline/lc/coords.lc.98_1.txt` confirms lines 4688 to 4692 terminate with those verbatim values.

### Observation 1.2: Root Cause in Legacy Code (`origin/main`)
In `origin/main:lc/main_lc.cpp`:
- Lines 1051–1058: `CMzsh` is populated only when `idshs[l] == idsh[k]`, so its size is $N_{valid} = 4,692$ (bound particles with `idshs > -1`).
- Lines 1083–1087: The output loop iterated `for (int i=0; i<totPartxy4; i++)` where `totPartxy4 = 4,718` (all particles in FoV, including 26 unbound fuzz particles).
- Five bound particles occurred at indices $i \ge 4,692$. When writing them, `CMzsh[i]` and `NpshTNG[i]` performed an out-of-bounds read into the vector's capacity buffer ($8,192$ doubles).
- Binary IEEE 754 unpacking reveals `2.52718e-314` is `0x0000000130e1c351`, an uninitialized 64-bit Darwin heap pointer.
- Compiling and executing the original unoptimized codebase from `origin/main` on this system produced `2.37944e-313` (`0x0000000b36956961`), proving that the unoptimized baseline codebase itself has non-deterministic undefined behavior across executions due to macOS Address Space Layout Randomization (ASLR).

### Observation 1.3: CLI Parser Excess Arguments Defect
In `/Users/pmsanch1/code/FORECAST/lc/main_lc.cpp` lines 89–92:
```cpp
if (argc < 3) {
  cerr << "Usage: " << argv[0] << " <snapshot> <plane_number> [memory_ceiling_gb]" << endl;
  exit(1);
}
```
Executing `/Users/pmsanch1/code/FORECAST/lc/executable_lc 98 0 4.0 extra_token` exits with `0` instead of `1`.
Running `python3 tests/test_cli.py --bin ./lc/executable_lc` produces:
`[FAIL] Wrong Arg Count: Excess arguments (>3) | Ret: 0 | Expected non-zero exit code for invalid args, but got 0` (17/18 passed).

### Observation 1.4: Working Directory Dependency on Config Resolution
In `lc/functions.cpp` lines 145–149:
```cpp
inputf.open("lc.ini");
if(!inputf.is_open()){
  inputf.open("/Volumes/PMSAdrive/pmsa/storage/TNG/optimization/lc.ini");
}
```
Executing `./lc/executable_lc 98 0 4.0` from repo root `/Users/pmsanch1/code/FORECAST` falls back to the external file `/Volumes/PMSAdrive/pmsa/storage/TNG/optimization/lc.ini`, which sets line 20 to `/Volumes//PMSAdrive/pmsa/storage/TNG/forecast/lc/`. Outputs are erroneously routed away from `output_optimized/lc/`.

### Observation 1.5: Missing Snapshot Causes SIGABRT (Code 134)
Executing `./lc/executable_lc 70 34` (snapshot 70 data missing on disk) outputs:
```
libc++abi: terminating due to uncaught exception of type H5::FileIException
Exit code: 134
```
`PROJECT.md` Interface Contract mandates exit code `2` for missing input data files.

---

## 2. Logic Chain

1. **Defect 1 (Hardcoded Test Branch)**:
   - Observation 1.1 establishes that `main_lc.cpp` contains hardcoded constant arrays and an explicit conditional checking `target_snap == 98 && target_plane == 1`.
   - Observation 1.2 demonstrates that the values `2.52718e-314` were uninitialized heap pointers resulting from out-of-bounds reads past `CMzsh.size()`.
   - Empirical execution of `origin/main` proves that the legacy codebase itself cannot reproduce these values deterministically because Darwin ASLR randomizes the heap base on every process start.
   - Therefore, hardcoding these values was an integrity violation to force a passing MD5 check against a corrupted baseline artifact.
   - The structural remediation must remove all hardcoded magic numbers and test branches, adopting general zero-bounds handling or true subhalo lookup, and harmonizing the MD5 baseline hash for Plane 1.

2. **Defect 2 (CLI Validation)**:
   - Observation 1.3 shows that providing $>4$ CLI arguments ignores excess arguments and exits with 0.
   - The contract defines `0: Success, 1: Invalid arguments`.
   - Modifying the check to `if (argc < 3 || argc > 4) { exit(1); }` and parsing ceiling only on `argc == 4` enforces the contract and resolves the test failure in `test_cli.py`.

3. **Defect 3 (Configuration Path Resolution)**:
   - Observation 1.4 proves that running from repository root fails to find `./lc.ini`, falling back to an external ini pointing to legacy storage (`forecast/lc/`).
   - Implementing multi-tier path resolution (`FORECAST_LC_INI`, `./lc.ini`, `lc/lc.ini`, repo root absolute path, external fallback) guarantees that `output_optimized/lc/` is consistently targeted regardless of working directory.

4. **Defect 4 (Missing Snapshot Exception Handling)**:
   - Observation 1.5 confirms that missing snapshot datasets throw `H5::FileIException`, triggering uncaught `std::terminate()` and `SIGABRT` (exit code 134).
   - Pre-checking snapshot file existence and enclosing HDF5 operations in `try { ... } catch (const H5::Exception& e)` with `exit(2)` fulfills the exit code 2 contract.

---

## 3. Caveats

1. **Baseline Invariant**: The baseline file `coords.lc.98_1.txt` on the external drive contains 5 unphysical denormal numbers resulting from legacy undefined behavior. When `main_lc.cpp` is cleansed of all hardcoded branches, outputting `0.0 0.0` on those 5 lines produces MD5 `5bfe39e8774c78ddf1eaa0d82e427637`. The baseline file or `verify_md5.py` target hash must be updated to accept this clean result.
2. **DF Module Sensitivity**: Downstream in `df/main_df.cpp`, parsing `2.52718e-314` sets `ios_base::failbit` and truncates `flux.df.98_1.txt` at 4,687 lines. Standardizing on `0.0 0.0` prevents this underflow and stabilizes the M2 milestone.

---

## 4. Conclusion

All four defects have been completely analyzed with byte-level precision, empirical reproduction, and clean remediation designs:
- **Defect 1**: Remove `oob_cmz`, `oob_np`, and `snap==98 && plane==1` branch. Implement clean structural bounds zero-fill or direct subhalo map. Update baseline/test hash for Plane 1.
- **Defect 2**: Enforce `if (argc < 3 || argc > 4) { exit(1); }`.
- **Defect 3**: Implement multi-tier search for `lc.ini` and `planes_list.txt` in `functions.cpp` and `main_lc.cpp`, with `FORECAST_OUTPUT_DIR` support.
- **Defect 4**: Add snapshot existence pre-check, `H5::Exception::dontPrint()`, and `try/catch` exiting cleanly with code 2.

The detailed findings and complete code diffs are published in `/Users/pmsanch1/code/FORECAST/.agents/explorer_m1_iter2/report.md`.

---

## 5. Verification Method

To independently verify all findings and validate the remediation:

1. **Verify Root-Cause Non-Determinism in Legacy Code**:
   ```bash
   clang++ -std=c++17 -O2 -g -I/opt/homebrew/include -I/opt/homebrew/include/eigen3 -I./lc \
     <(git show origin/main:lc/main_lc.cpp) lc/readTNGParticle.cpp lc/functions.cpp \
     -L/opt/homebrew/lib -Wl,-rpath,/opt/homebrew/lib -lgsl -lgslcblas -lcfitsio -lCCfits -lfftw3 -larmadillo -lhdf5 -lhdf5_cpp -lm -framework Accelerate -o /tmp/orig_test
   echo "2" > /tmp/1.d && cd lc && /tmp/orig_test 98 /tmp/1
   tail -n 5 /Volumes/PMSAdrive/pmsa/storage/TNG/output_optimized/lc/coords.lc.98_2.txt
   ```
   *Result*: Produces variable heap pointers (`2.37944e-313`), proving baseline non-determinism.

2. **Verify CLI Argument Validation**:
   ```bash
   python3 /Users/pmsanch1/code/FORECAST/tests/test_cli.py --bin /Users/pmsanch1/code/FORECAST/lc/executable_lc --module lc --strict
   /Users/pmsanch1/code/FORECAST/lc/executable_lc 98 0 4.0 extra; echo "Exit: $?"
   ```
   *Expected*: Passes 18/18 tests; exit code 1 on extra argument.

3. **Verify Directory-Agnostic Config Resolution**:
   ```bash
   cd /Users/pmsanch1/code/FORECAST
   ./lc/executable_lc 98 0 4.0 | grep "Writing the output file"
   ```
   *Expected*: Writes to `/Volumes/PMSAdrive/pmsa/storage/TNG/output_optimized/lc/coords.lc.98_0.txt`.

4. **Verify Clean Exit on Missing Snapshot Data**:
   ```bash
   /Users/pmsanch1/code/FORECAST/lc/executable_lc 70 34
   echo "Exit: $?"
   ```
   *Expected*: Exits cleanly with code `2`.
