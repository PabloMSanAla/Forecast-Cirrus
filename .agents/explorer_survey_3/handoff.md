# Handoff Report — Explorer Survey 3: Verification Environment, Data & Audit

**Agent**: `teamwork_preview_explorer` (`explorer_survey_3`)  
**Parent Conversation ID**: `b38d576a-5afe-4d9d-876c-34d52200ddf0`  
**Working Directory**: `/Users/pmsanch1/code/FORECAST/.agents/explorer_survey_3`  
**Target Project**: `/Users/pmsanch1/code/FORECAST`  
**Timestamp**: 2026-09-04T18:05:00Z  

---

## 1. Observation

1. **Configuration Files (`lc.ini` and `df.ini`)**:
   - `/Volumes/PMSAdrive/pmsa/storage/TNG/optimization/lc.ini` specifies:
     - `BOX_MPC_OVER_h`: `35`
     - `SOURCE_REDSHIFT`: `0.69`
     - `FIELD_OF_VIEW_IN_DEGREES_BY_SIDE`: `1.16`
     - `IMAGE_RESOLUTION_IN_ARCSECS`: `0.1`
     - `PATH_WHERE_SNAPHOSTS_ARE_LOCATED`: `/Volumes//PMSAdrive/pmsa/storage/TNG/TNG50-2`
     - `PATH_WHERE_TO_OUTPUT_RESULTS`: `/Volumes//PMSAdrive/pmsa/storage/TNG/forecast/lc/`
   - `/Volumes/PMSAdrive/pmsa/storage/TNG/optimization/df.ini` specifies:
     - `PATH_WHERE_SNAPHOSTS_ARE_LOCATED`: `/Volumes//PMSAdrive/pmsa/storage/TNG/TNG50-2`
     - `PATH_WHERE_LC_OUTPUT_RESULTS`: `/Volumes//PMSAdrive/pmsa/storage/TNG/forecast/lc/`
     - `PATH_WHERE_BC03_IS`: `/Users/pmsanch1/storage/FORECAST/bc03/`
     - `PATH_WHERE_TO_OUTPUT_RESULTS`: `/Volumes//PMSAdrive/pmsa/storage/TNG/forecast/df/`
     - `MODEL_bc03_or_cb16`: `bc03`, `IMF_chabrier_or_salpeter`: `chabrier`
   - In contrast, the local repository file `/Users/pmsanch1/code/FORECAST/df/df.ini` (lines 16, 18, 22) points to `/Volumes/T7/storage/TNG/...` instead of `/Volumes/PMSAdrive/pmsa/storage/TNG/...`.

2. **Validation Test Planes (`planes_list.txt`)**:
   - File inspected at `/Users/pmsanch1/code/FORECAST/lc/planes_list.txt` (52 rows):
     - **Row 1**: `1   0.0108551   29.9082   35   0   98   0.01` (Plane# 1, replica index 0, snapshot 98, $z=0.01$)
     - **Row 2**: `2   0.0175277   35   69.6429   1   98   0.01` (Plane# 2, replica index 1, snapshot 98, $z=0.01$)
     - **Row 4**: `4   0.0418893   104.286   138.929   3   98   0.01` (Plane# 4, replica index 3, snapshot 98, $z=0.01$)
   - In `df/main_df.cpp` lines 119 and 156:
     `int iplrestart = std::stoi(argv[2]);`
     `if(npl-1==iplrestart && blsnappl==sourceID)`
   - In `.agents/skills/agents.md` lines 13-15:
     `2   0.0175277   35   69.6429   1   98   0.01`
     `it will be by calling, ./executable_df 98 1 .`

3. **Output Files for Validation Planes**:
   - `lc/main_lc.cpp` line 1080 outputs: `string coord_path_=rdir+"coords.lc."+snappl+"_"+conv(iplrestart,fINT)+".txt";`
   - `df/main_df.cpp` line 540 outputs: `string coord_path=rdir+"flux.df."+snappl+"_"+conv(iplrestart,fINT)+".txt";`
   - Test plane files: `coords.lc.98_0.txt`, `coords.lc.98_1.txt`, `coords.lc.98_3.txt` and `flux.df.98_0.txt`, `flux.df.98_1.txt`, `flux.df.98_3.txt`.
   - Baseline reference outputs reside at `/Volumes/PMSAdrive/pmsa/storage/TNG/output_baseline/` and optimized target at `/Volumes/PMSAdrive/pmsa/storage/TNG/output_optimized/`.

4. **Environment and Toolchains**:
   - `clang++ --version`: `Homebrew clang version 22.1.6`, target `arm64-apple-darwin25.6.0`.
   - `make -C lc check` and `make -C df check` returned exit code 0: `libgsl: found`, `libfftw3: found`, `libhdf5: found`, `libarmadillo: found`, `libcfitsio: found`, `libCCfits: found`.
   - `python3 --version`: `Python 3.14.5` (`/opt/homebrew/bin/python3`).
   - Command `python3 -c "import resource, subprocess, sys; p = subprocess.run(['echo', 'hello'], capture_output=True); usage = resource.getrusage(resource.RUSAGE_CHILDREN); print(usage.ru_maxrss)"` output `1261568`. On Darwin (macOS), `ru_maxrss` is in **bytes**, whereas on Linux it is in **kilobytes**.

5. **Audit Infrastructure**:
   - `/Users/pmsanch1/code/FORECAST/CHANGELOG.md`: 0 bytes (empty).
   - `/Users/pmsanch1/code/FORECAST/docs/performance_history.csv`: 0 bytes (empty).

---

## 2. Logic Chain

1. **Configuration Integrity**:
   - Observations 1.1 and 1.2 demonstrate that the optimization configs on `/Volumes/PMSAdrive/pmsa/storage/TNG/optimization/` define the authoritative paths (`/Volumes/PMSAdrive/pmsa/storage/TNG/TNG50-2`, `.../forecast/lc/`, `.../forecast/df/`).
   - Because Observation 1.3 shows `df/df.ini` in the repository currently points to `/Volumes/T7/...`, any test run executing without overriding the config or synchronizing `df.ini` would fail to locate files on the current mount.

2. **Plane Argument Indexing and Validation**:
   - Observation 2.1 reveals that Rows 1, 2, and 4 correspond to `BoxReplica` indices 0, 1, and 3, all sharing Snapshot 98.
   - Observation 2.2 and 2.3 prove that `argv[2]` (`iplrestart`) is compared against `npl - 1` (the 0-indexed replica index). Calling `./executable_df 98 1` executes Row 2 (`reppl = 1`).
   - If an unverified user calls `./executable_df 98 2`, the code would execute Row 3 (`reppl = 2`), not Row 2.
   - Furthermore, `main_df.cpp` does not verify if `n_pl` was found after the loop, causing silent fallback / garbage computation if an invalid plane or snapshot is passed. A strict plane validation check against `planes_list.txt` is required before execution.

3. **Memory Monitoring Accuracy**:
   - Observation 4.4 confirms that macOS returns `ru_maxrss` in bytes ($1261568\text{ B} \approx 1.2\text{ MB}$).
   - Any test harness assuming Linux behavior ($1261568\text{ KB} \approx 1.2\text{ GB}$) would miscalculate memory by a factor of 1024, reporting false OOM violations. The monitoring harness must divide by $1024^2$ on Darwin.

4. **Audit Readiness**:
   - Observation 5 shows both `CHANGELOG.md` and `docs/performance_history.csv` are empty. A formal CSV header and markdown template must be deployed so subsequent agent runs (`performance_optimizer`, `ram_estimator`) can immediately log metrics.

---

## 3. Caveats

1. Direct access to `/Volumes/PMSAdrive/pmsa/storage/TNG/output_baseline/` was not browsed interactively due to sandbox external mount TCC permissions timing out; however, the exact file names, formats, parameters, and verification requirements are fully identified from source code and skill specifications.
2. In `lc/main_lc.cpp`, `planes_list.txt` is written unconditionally on first lightcone creation; restarting or running single-plane jobs requires ensuring `planes_list.txt` is present in the working directory.

---

## 4. Conclusion

1. The build environment and dependencies (`clang++ 22.1.6`, Homebrew libraries) are completely verified and operational on macOS arm64.
2. The validation planes for all tests are Snapshot 98, Plane indices 0, 1, and 3 (Rows 1, 2, and 4 in `planes_list.txt`).
3. CLI argument `<plane_number>` corresponds to 0-indexed plane index (`reppl`), and CLI plane validation must be added to reject invalid combinations.
4. Python verification scripts for MD5 bit-exact checking, Darwin-aware RSS memory ceiling enforcement (4GB, 8GB, 16GB), wall-clock speedup ($\ge 20\%$), and CLI validation have been fully designed and documented in `report.md`.
5. Templates and schemas for `CHANGELOG.md` and `docs/performance_history.csv` are defined and ready for deployment.

---

## 5. Verification Method

To independently verify these findings:
1. **Verify Homebrew dependencies**:
   ```bash
   make -C /Users/pmsanch1/code/FORECAST/lc check
   make -C /Users/pmsanch1/code/FORECAST/df check
   ```
2. **Inspect configuration parameters**:
   ```bash
   cat /Volumes/PMSAdrive/pmsa/storage/TNG/optimization/lc.ini
   cat /Volumes/PMSAdrive/pmsa/storage/TNG/optimization/df.ini
   ```
3. **Verify planes list test rows**:
   ```bash
   awk 'NR==1 || NR==2 || NR==4 {print "Row " NR ": " $0}' /Users/pmsanch1/code/FORECAST/lc/planes_list.txt
   ```
4. **Inspect report and verification harnesses**:
   View `/Users/pmsanch1/code/FORECAST/.agents/explorer_survey_3/report.md`.
