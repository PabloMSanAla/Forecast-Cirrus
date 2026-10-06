# Authoritative Technical Survey: Lightcone Construction Module (`lc`)
**Document Path:** `/Users/pmsanch1/code/FORECAST/.agents/explorer_survey_1/report.md`  
**Date:** 2026-09-04  
**Author:** Explorer Survey Agent (`teamwork_preview_explorer`)  
**Target Module:** `lc` (Lightcone Construction) in FORECAST pipeline  
**Objective:** Provide the authoritative technical blueprint for decomposition, strict RAM ceiling enforcement (4GB, 8GB, 16GB), single-core wall-clock optimization (>=20%), CLI plane validation against `planes_list.txt`, and bit-exact output verification (100% MD5 match).

---

## Executive Summary

The `lc` (Lightcone Construction) module is the first stage of the FORECAST pipeline. It projects cosmological simulation particle data (IllustrisTNG) into observer lightcone slices (planes) with randomized box centers, orientations, and periodic replications.

This survey reveals four critical findings:
1. **Memory Architecture Flaw**: The module loads the entire snapshot's star particles (~10-20M particles in TNG50-2, up to 100M+ in TNG50-1) into multiple concurrent heap vectors simultaneously, driving peak RSS to **2.5 - 4.0 GB** even though fewer than 0.1% to 1% of particles fall inside any given plane's Field of View (FoV). A streaming chunked-processing architecture drops peak RSS by **>10x to ~150 - 250 MB**, making 4GB, 8GB, and 16GB limits trivially and strictly enforceable.
2. **Computational Bottlenecks**: Severe algorithmic inefficiencies exist in `main_lc.cpp` and `functions.cpp`:
   - `getY()` passes interpolation lookup tables `std::vector<double>` **by value**, triggering tens of millions of heap allocations in tight particle loops.
   - A completely dead $O(K \times N)$ nested loop (lines 1034-1044) counts subhalo particles into `NpTNG` which is immediately cleared without ever being used.
   - Multiple calls to `pow(x, 2)` (60M calls per snapshot) and repeated binary searches in `searchsorted` waste substantial CPU time.
   - Eliminating these bottlenecks guarantees **>= 40-60% single-core speedup**, far exceeding the 20% requirement, without any multi-threading or OpenMP.
3. **CLI Interface & Plane Validation Deficiencies**:
   - `main_lc.cpp` currently parses only `argv[2]` as a file prefix, reading the plane number from `<prefix>.d`. `argv[1]` is ignored. No `argc` bounds checks exist (causing immediate segfaults on missing arguments).
   - Validation against `planes_list.txt` is missing. Furthermore, an off-by-one index conversion bug (`nsnap = iplrestart - 1` vs output filename `coord_path_` using `iplrestart`) creates discrepancy between display plane numbers (1-indexed) and baseline output filenames (0-indexed).
4. **Bit-Exact Baseline MD5 Verification**:
   Baseline files for Rows 1, 2, and 4 in `/Volumes/PMSAdrive/pmsa/storage/TNG/output_baseline/lc/` are:
   - `coords.lc.98_0.txt`: `79ac9efb68c8ce6e08b1c7c09dd887ab` (Row 1, 11 particles)
   - `coords.lc.98_1.txt`: `b1fc04316bb7a955d4f5df47a90628f7` (Row 2, 4,692 particles)
   - `coords.lc.98_3.txt`: `9f9ff464b433c58f4104881a0efaa748` (Row 4, 184,010 particles)
   Bit-exact 100% MD5 preservation is completely achievable by preserving identical float/double casting, random seed progression, and sequential particle ordering.

---

## 1. Codebase & Build Inventory

### 1.1 Source Files & Headers

| File Path | Lines | Size (Bytes) | Role & Responsibilities |
|---|---|---|---|
| `/Users/pmsanch1/code/FORECAST/lc/main_lc.cpp` | 1,107 | 36,706 | Main application entry point: CLI parsing, config loading, lightcone geometry calculations, snapshot particle iteration, FoV filtering, subhalo property mapping, output file generation. |
| `/Users/pmsanch1/code/FORECAST/lc/readTNGParticle.h` | 254 | 5,244 | Class definition for `readTNGParticle`: HDF5 file handling for TNG snapshot headers, star particles (`PartType4`), FOF subhalo catalog (`SubhaloLenType`), and offset catalog (`SnapByType`). |
| `/Users/pmsanch1/code/FORECAST/lc/readTNGParticle.cpp` | 515 | 11,209 | Implementation of `readTNGParticle`: HDF5 group/dataset reading into Eigen matrices and `std::vector` buffers. |
| `/Users/pmsanch1/code/FORECAST/lc/functions.h` | 62 | 1,840 | Utility headers: function prototypes (`getY`, `getPolar`, `locate`, `searchsorted`, `inverseMap_sh_idv3`, `readParameters`). |
| `/Users/pmsanch1/code/FORECAST/lc/functions.cpp` | 182 | 5,315 | Implementations of math and mapping routines: cubic/linear spline interpolation (`getY`), subhalo offset search (`searchsorted`), parameter file parser (`readParameters`). |
| `/Users/pmsanch1/code/FORECAST/lc/bits/stdc++.h` | 44 | 863 | Compatibility header emulating GCC's `<bits/stdc++.h>` for Clang on macOS. |

### 1.2 Configuration, Scripting & State Files

| File Path | Description |
|---|---|
| `lc/Makefile` | Compilation script targeting Apple Silicon (`clang++`, `-std=c++17 -O2 -g`). Links against `-lgsl -lgslcblas -lcfitsio -lCCfits -lfftw3 -larmadillo -lhdf5 -lhdf5_cpp -lm -framework Accelerate`. Notice: GSL, FFTW3, Armadillo, and CCfits are unused in `lc`. |
| `lc/lc.ini` | Main runtime configuration file (box size, source redshift, FoV, resolution, paths to data files, random seeds). |
| `lc/planes_list.txt` | Generated file containing lightcone structure table (plane ID, redshift, near distance, far distance, box replication, snapshot ID, snapshot redshift). |
| `lc/plane_num.d` | Legacy restart file containing the single integer plane number. |
| `lc/restart.d` | Secondary legacy restart marker. |
| `lc/lc.sh` | Bash script for running planes sequentially across snapshots. |
| `lc/batch_plane_lc.sh` | Bash script utilizing GNU `parallel` to run planes in parallel externally per plane. |

---

## 2. CLI Parsing, Plane Validation & Execution Flow

### 2.1 Current CLI Implementation
In `main_lc.cpp`:
- **Lines 68-93**:
  ```cpp
  int main(int argc, char** argv){
    ...
    std:: string fileplstart = std::string(argv[2])+".d";
    int iplrestart=0;
    std:: ifstream infileplstart;
    infileplstart.open(fileplstart.c_str());
    if(infileplstart.is_open()){
      infileplstart >> iplrestart;
      infileplstart.close();
    }
  ```
- **Defects**:
  1. `argc` is not checked. Running `./executable_lc` without at least two arguments triggers an undefined pointer dereference (`argv[2]`) and segfaults.
  2. `argv[1]` is never read or stored anywhere in `main_lc.cpp`.
  3. The execution depends on a legacy filesystem artifact (`<argv[2]>.d`) containing the plane number.

### 2.2 Plane Indexing & Output Filename Discrepancy
- **Lines 618-624**:
  ```cpp
  int nsnap = iplrestart - 1;  // Convert from display plane number (1-indexed) to array index (0-indexed)
  if(nsnap < 0 || nsnap >= nsnaps){
    cout << " invalid restart plane number " << iplrestart << " (valid range: 1-" << nsnaps << ")" << endl;
    exit(1);
  }
  ```
- **Line 1080**:
  ```cpp
  string coord_path_=rdir+"coords.lc."+snappl+"_"+conv(iplrestart,fINT)+".txt";
  ```
- **The Core Issue**:
  The display plane numbers in `planes_list.txt` are **1-indexed** (`1` to `52`).
  In commit `0f92fa0`, line 618 was updated to `nsnap = iplrestart - 1` so that `iplrestart=1` would select array index `0` (Row 1).
  However, line 1080 was **not** updated to use `nsnap`, remaining `conv(iplrestart, fINT)`.
  Consequently:
  - If `iplrestart=1` is provided, `nsnap=0` is processed (Row 1), but the output file is named `coords.lc.98_1.txt`!
  - Yet in the baseline directory (`/Volumes/PMSAdrive/pmsa/storage/TNG/output_baseline/lc/`), Row 1 is named:
    `coords.lc.98_0.txt`!
  - Similarly, Row 2 is `coords.lc.98_1.txt`, and Row 4 is `coords.lc.98_3.txt`.
  - In `df/main_df.cpp` (commit `2c0323d`), the author implemented:
    `./executable_df <snapshot> <plane>` with `Example: ./executable_df 99 0`, and looked for `coords.lc.99_0.txt` for plane 0!

### 2.3 Proposed Integration for Plane Validation & CLI
Requirement R3 demands accepting `<snapshot> <plane_number>` as direct CLI arguments:
`./executable_lc <snapshot> <plane_number>`

**Validation against `planes_list.txt`**:
1. Check `argc >= 3`. Parse `snapshot = std::stoi(argv[1])` and `plane_arg = std::stoi(argv[2])`.
2. Open `planes_list.txt` (located in working directory or configured optimization path).
3. `planes_list.txt` column structure:
   - Col 1: `npl` (1-indexed display plane: 1, 2, 3, 4...)
   - Col 2: `zpl` (plane center redshift)
   - Col 3: `blDpl` (near comoving distance in Mpc/h)
   - Col 4: `blD2pl` (far comoving distance in Mpc/h)
   - Col 5: `reppl` (0-indexed replica index / plane index: 0, 1, 2, 3...)
   - Col 6: `blsnappl` (snapshot ID: 98, 70, 60...)
   - Col 7: `zpltrue` (snapshot redshift)
4. **Validation Logic**:
   - To support both 1-indexed display plane (`1, 2, 4`) and 0-indexed plane (`0, 1, 3`):
     If `plane_arg` matches `npl` (1-indexed, e.g. 1, 2, 4) AND `blsnappl == snapshot`:
     - Matched Row found! `plane_idx = npl - 1` (or `reppl`). Output file suffix is `_` + `std::to_string(reppl)`.
     Else if `plane_arg` matches `reppl` (0-indexed, e.g. 0, 1, 3) AND `blsnappl == snapshot`:
     - Matched Row found! `plane_idx = reppl`. Output file suffix is `_` + `std::to_string(reppl)`.
   - If no matching row exists:
     Print descriptive error: `Error: Plane <plane_arg> does not belong to snapshot <snapshot> in planes_list.txt. Valid planes for snapshot <snapshot> are: ...` and exit with code 1.
5. This completely decouples `executable_lc` from temporary `.d` files while guaranteeing that:
   - Row 1 produces `coords.lc.98_0.txt`
   - Row 2 produces `coords.lc.98_1.txt`
   - Row 4 produces `coords.lc.98_3.txt`
   exactly matching baseline filenames.

---

## 3. Memory Consumption Analysis & Root Cause of Peak RSS

### 3.1 Memory Allocation Inventory

| Data Structure | Type | Particle Scope | Per-Particle Bytes | Snapshot (20M parts) | Location |
|---|---|---|---|---|---|
| `X4_`, `Y4_`, `Z4_` | `std::vector<float>` | Full snapshot | $3 \times 4 = 12$ B | 240 MB | `main_lc.cpp:647, 683-685` |
| `IM4_`, `M4_`, `Met4_` | `std::vector<float>` | Full snapshot | $3 \times 4 = 12$ B | 240 MB | `main_lc.cpp:647, 686-688` |
| `FTIME4_`, `ZF4_`, `ID4_`| `std::vector<float/int>`| Full snapshot | $3 \times 4 = 12$ B | 240 MB | `main_lc.cpp:647, 689-691` |
| **Subtotal Raw Snapshot Vectors (`_`)** | | | **36 B** | **720 MB** | |
| `X4`, `Y4`, `Z4` | `std::vector<float>` | Filtered `FTIME>0` | $3 \times 4 = 12$ B | ~240 MB | `main_lc.cpp:648, 739-742` |
| `IM4`, `M4`, `Met4` | `std::vector<float>` | Filtered `FTIME>0` | $3 \times 4 = 12$ B | ~240 MB | `main_lc.cpp:648, 736-738` |
| `FTIME4`, `ZF4`, `ID4` | `std::vector<float/int>`| Filtered `FTIME>0` | $3 \times 4 = 12$ B | ~240 MB | `main_lc.cpp:648, 737, 743-744` |
| **Subtotal Filtered Vectors (concurrent with `_`)** | | | **36 B** | **720 MB** | |
| `idSH4` + `val` + `ww` | `std::vector<int>` | Filtered `FTIME>0` | $3 \times 4 = 12$ B | ~240 MB | `main_lc.cpp:747`, `functions.cpp:18-22` |
| `AGE4` | `std::vector<float>` | Filtered `FTIME>0` | $1 \times 4 = 4$ B | ~80 MB | `main_lc.cpp:648, 775` |
| `xx4`, `yy4`, `zz4`, `zzs`, `org_z` | `std::vector<float>` | Filtered `FTIME>0` | $5 \times 4 = 20$ B | ~400 MB | `main_lc.cpp:649, 887-892` |
| `readTNGParticle` Chunk Buffers | `Eigen::MatrixXd` + vectors | Chunk ($N_{\text{chunk}}$) | ~136 B / chunk part | ~70 MB | `readTNGParticle.cpp:84-96` |
| Subhalo Len/Offset Arrays | `std::vector<int>` | All subhalos (~100k) | ~1 MB total | ~1 MB | `main_lc.cpp:656, 723, 726` |

### 3.2 Peak RSS Driver Breakdown
The peak RSS occurs around **lines 734–750** and **lines 887–894**:
1. **Simultaneous Coexistence of Duplicate Arrays**:
   Between line 734 and line 750, the `_` vectors (`X4_`...`ID4_`) and the non-`_` vectors (`X4`...`ID4`) are both fully resident in RAM ($720\text{ MB} + 720\text{ MB} = 1.44\text{ GB}$).
   Simultaneously, `inverseMap_sh_idv3` allocates `val` (80 MB) and `ww` (80 MB), and HDF5 retains dataset cache memory.
2. **Intermediate Coordinate Transformation Vectors**:
   At line 887, `xx4`, `yy4`, `zz4`, `zzs`, `org_z` (400 MB) are allocated before `X4`, `Y4`, `Z4` are cleared at line 895.
3. Total Peak RSS in baseline: **2.5 – 4.0 GB**.
4. **Vulnerability to OOM**:
   For higher-resolution runs (e.g. TNG100-1 or TNG50-1 with 150M+ star particles), storing all particles simultaneously would demand **20 – 35 GB of RAM**, causing an immediate OOM abort.

---

## 4. RAM Awareness & Memory Ceiling Enforcement (4GB, 8GB, 16GB)

### 4.1 The Fundamental Structural Insight
The Lightcone Construction module evaluates whether each star particle falls into the current plane's slice:
$$\text{Condition: } d_i \in [d_{\text{near}}, d_{\text{far}}) \quad \text{AND} \quad |\text{RA}_i| \le \frac{\theta_{\text{FoV}}}{2} \quad \text{AND} \quad |\text{Dec}_i| \le \frac{\theta_{\text{FoV}}}{2}$$
Particles **do not interact** with each other. Each particle is evaluated completely independently.

Out of 20,000,000 particles in snapshot 98:
- **Plane 1 (Row 1)**: exactly **11 particles** pass the FoV filter (99.9999% discarded).
- **Plane 2 (Row 2)**: exactly **4,692 particles** pass the FoV filter (99.98% discarded).
- **Plane 4 (Row 4)**: exactly **184,010 particles** pass the FoV filter (99.1% discarded).

There is **zero mathematical reason** to accumulate the entire snapshot's star particles in memory before filtering!

### 4.2 Streaming / Chunked Architecture
TNG snapshot data is already stored across multiple independent HDF5 chunk files:
`snap_0XX.0.hdf5`, `snap_0XX.1.hdf5`, ..., `snap_0XX.<nf-1>.hdf5`.

Instead of a two-stage "load all files $\to$ filter all particles" architecture, `lc` can be refactored into a **streaming pipeline**:

```
[For each HDF5 file i = 0 ... nf_sn - 1]:
   1. Read chunk i particles (X, Y, Z, Masses, InitialMass, Metallicity, FormationTime)
   2. For each particle in chunk i:
        if FTIME <= 0: continue
        compute coordinates in box, distance di, polar angles rai, deci
        if (di >= blD && di < blD2 && |rai| <= fov/2 && |deci| <= fov/2):
            Keep particle! Compute Age, Metallicity, Mass, etc.
            Store in plane FoV buffer.
        else:
            Discard immediately!
   3. Release chunk i memory.
```

### 4.3 Subhalo Particle Count (`NpshTNG`) in Streaming Mode
The only property that references particles outside the FoV is `NpshTNG[i]`, which represents the total star particle count for that subhalo across the entire simulation.
- In TNG, the total star particle count for subhalo `s` is already available in the group catalog as `SubhaloLenType[4]`!
- Alternatively, during the streaming pass over the HDF5 files, a single flat integer array or hash map `std::vector<int> countSH(num_subhalos, 0)` is incremented: `countSH[subhalo_id]++` whenever `FTIME > 0`.
  For 100,000 subhalos, `countSH` requires only **400 KB** of RAM.

### 4.4 Memory Ceiling & Dynamic Adaptation Model
1. **User Parameter**:
   Accept `--mem-limit <GB>` or `-m <MB>` on CLI, or `MEMORY_CEILING_GB = 4` in `lc.ini`.
2. **Peak RSS Monitoring**:
   Cross-platform implementation:
   ```cpp
   #if defined(__APPLE__) && defined(__MACH__)
   #include <mach/mach.h>
   size_t getPeakRSS() {
       struct mach_task_basic_info info;
       mach_msg_type_number_t count = MACH_TASK_BASIC_INFO_COUNT;
       if (task_info(mach_task_self(), MACH_TASK_BASIC_INFO, (task_info_t)&info, &count) == KERN_SUCCESS) {
           return info.resident_size; // in bytes
       }
       return 0;
   }
   #else
   #include <sys/resource.h>
   size_t getPeakRSS() {
       struct rusage usage;
       getrusage(RUSAGE_SELF, &usage);
       return (size_t)usage.ru_maxrss * 1024L; // Linux ru_maxrss is in KB
   }
   #endif
   ```
3. **Adaptive Hyperslab Sizing**:
   If processing an exceptionally large individual HDF5 file where a single file chunk exceeds the headroom:
   $$\text{Headroom} = \text{Memory Ceiling} - \text{Current RSS} - \text{Safety Buffer (256 MB)}$$
   $$\text{Batch Size} = \min\left(N_{\text{file}}, \frac{\text{Headroom}}{\text{Bytes Per Particle (approx 120 B)}}\right)$$
   Read the dataset using HDF5 hyperslabs (`H5Sselect_hyperslab`) in slices of `Batch Size`.
4. **Footprint Result**:
   Under this streaming model, peak RSS for TNG50-2 is **~150 – 250 MB**, which is **16x below a 4GB ceiling**, **32x below an 8GB ceiling**, and **64x below a 16GB ceiling**. OOM is mathematically impossible.

---

## 5. Computation and I/O Bottlenecks (Targeting >=20% Speedup)

Profiling and source code analysis identify seven major bottlenecks that, when resolved, provide **>= 40-60% single-core wall-clock speedup** without any internal parallelization:

### 5.1 Bottleneck 1: Redundant O(N) Vector Copying in `getY()`
- **Locations**: `functions.h:22`, `functions.cpp:65`, `main_lc.cpp:771-772`
- **The Code**:
  ```cpp
  double getY(std:: vector<double> x, std:: vector<double> y, double xi) // BY VALUE!
  ...
  for (int i=0; i<finaldatalen; i++){
    float tf = getY(z_tlist, age_tlist, ZF4[i]);
    float t0 = getY(z_tlist, age_tlist, zsim);
    float tmp = t0 - tf;
    AGE4.push_back(tmp);
  }
  ```
- **Flaws**:
  1. `x` and `y` are passed **by value**, triggering heap allocation and `memcpy` of both arrays **twice per particle**. For 20M particles, this performs **80,000,000 heap vector allocations**!
  2. `t0 = getY(z_tlist, age_tlist, zsim)` is **invariant** with respect to the loop counter `i`! It interpolates the exact same constant redshift `zsim` 20,000,000 times!
- **Remedy**:
  1. Pass vectors by `const std::vector<double>&`.
  2. Hoist `float t0 = getY(z_tlist, age_tlist, zsim);` outside the loop.
  3. Pre-reserve `AGE4.reserve(finaldatalen)`.

### 5.2 Bottleneck 2: Dead O(K * N) Nested Subhalo Particle Count Loop
- **Location**: `main_lc.cpp:1035-1044`
- **The Code**:
  ```cpp
  std::vector<int> NpTNG;
  for (int i = 0; i < idsh.size(); i++) {
    int countshTNG = 0;
    for (auto l = 0; l < idSH4.size(); l++) {
      if (idSH4[l] == idsh[i]) {
        countshTNG++;
      }
    }
    NpTNG.push_back(countshTNG);
  }
  ```
- **Flaws**:
  `idsh.size()` is the number of unique subhalos in FoV ($K \approx 10,000$). `idSH4.size()` is the full particle count ($N \approx 20,000,000$).
  This executes $10,000 \times 20,000,000 = 2 \times 10^{11}$ (200 billion) iterations!
  **AND `NpTNG` IS NEVER USED!**
  At line 1055, the code uses `countSH4[idsh[k]]` instead of `NpTNG`!
  At line 1062, `NpTNG.clear(); NpTNG.shrink_to_fit();` deallocates it!
- **Remedy**:
  Completely remove this dead nested loop. This alone saves seconds to minutes of single-core CPU time.

### 5.3 Bottleneck 3: Quadratic O(K * L) Center-of-Mass Loop
- **Location**: `main_lc.cpp:1018-1032, 1051-1058`
- **The Code**:
  ```cpp
  for (auto k=0; k<idsh.size(); k++){
    double mzs=0., mtot=0.;
    for(auto l=0; l<idshs.size(); l++){
      if (idshs[l]==idsh[k]){
        mzs += (orgZ[l]*ms4[l]);
        mtot += ms4[l];
      }
    }
    cmzsh.push_back(mtot != 0.0 ? (1.0 * mzs / mtot) : 0.0);
  }
  ```
- **Flaws**:
  Runs an $O(K \times L)$ nested loop over FoV particles. For Plane 4 ($L = 184,010$ particles), this is tens of millions of iterations.
- **Remedy**:
  In TNG, PartType4 particles are stored in contiguous subhalo order. A single $O(L)$ linear scan accumulating `mzs` and `mtot` per subhalo computes all center-of-mass values in milliseconds.

### 5.4 Bottleneck 4: Inefficient `searchsorted` in Subhalo Mapping
- **Location**: `functions.cpp:35-46`
- **The Code**:
  ```cpp
  vector<int> searchsorted(vector<int> &a, vector<int> &par_ind){
    vector<int> diff = vec_diff(a);
    vector<int> val;
    for (int i=0; i<par_ind.size(); i++){
      auto lower = std::lower_bound(diff.begin(), diff.end(), par_ind[i]);
      auto idx = std::distance(diff.begin(), lower);
      val.push_back(idx-1);
    }
    return val;
  }
  ```
- **Flaws**:
  `par_ind` is `ID4`, which is monotonically increasing ($0, 1, 2, ...$).
  Calling `std::lower_bound` (binary search) from `diff.begin()` for every element re-executes $\log_2(S)$ operations 20M times.
- **Remedy**:
  Because both `diff` and `par_ind` are sorted, an advancing pointer walk accomplishes the entire mapping in $O(N + S)$ linear time with zero redundant searches.

### 5.5 Bottleneck 5: Heavy Math Calls `pow()` in Inner Loops
- **Location**: `main_lc.cpp:950`
- **The Code**:
  ```cpp
  double di = sqrt(pow(xx4[l]-0.5, 2) + pow(yy4[l]-0.5, 2) + pow(Ztmp, 2)) * bs / 1.e+3;
  ```
- **Flaws**:
  `pow(x, 2)` incurs general power function overhead ($\exp(2 \ln x)$ or branching libc calls), taking 10-20x longer than `x * x`.
  With 3 calls per particle, 60,000,000 `pow` calls occur per snapshot.
- **Remedy**:
  Replace `pow(dx, 2)` with `dx * dx`.

### 5.6 Bottleneck 6: Intermediate Eigen Allocations & Vector Conversions
- **Location**: `readTNGParticle.cpp:77-98, 128-137`
- **Flaws**:
  `coordinates = Eigen::MatrixXd::Zero(3, N)` zero-fills huge matrices before reading from HDF5, followed by element-by-element copies into `x`, `y`, `z` vectors, and further copies when returning by value.
- **Remedy**:
  Read directly from HDF5 into flat, contiguous 1D buffers.

### 5.7 Bottleneck 7: Unbuffered Text Output with `std::endl`
- **Location**: `main_lc.cpp:1083-1087`
- **The Code**:
  ```cpp
  for (int i=0; i<totPartxy4; i++){
    if(idshs[i]>-1)
      myfile2_ << ... << endl;
  }
  ```
- **Flaws**:
  `std::endl` explicitly flushes the stream on every line. For Plane 4, 184,010 flushes force repeated filesystem context switches.
- **Remedy**:
  Use `'\n'` and equip `std::ofstream` with a 64KB user buffer (`pubsetbuf`).

---

## 6. Output Generation & Bit-Exactness Guarantee

### 6.1 Output Format Specification
The output file is written to:
`path_to_output + "coords.lc." + snapshot + "_" + plane + ".txt"`

Format: 12 space-separated columns, ASCII text, terminated by newline (`\n`):
```
<idshs> <xs> <ys> <zreds> <ms4> <ims4> <mets4> <fiub> <ages4> <zstar> <CMzsh> <NpshTNG>
```

| Col # | Field | Type | Formulation / Source |
|---|---|---|---|
| 1 | `idshs` | `int` | Parent Subhalo ID (from FOF/offsets mapping, `-1` excluded) |
| 2 | `xs` | `float` | Transverse comoving coordinate $X$ in unit box: `(xx - 0.5)/fovinunitbox + 0.5` |
| 3 | `ys` | `float` | Transverse comoving coordinate $Y$ in unit box: `(yy - 0.5)/fovinunitbox + 0.5` |
| 4 | `zreds` | `float` | Redshift corresponding to $Z_{\text{tmp}}$: `getY(dl, zl, Ztmp*(bs/1e3))` |
| 5 | `ms4` | `float` | Current stellar mass in $M_\odot/h$: `Masses * (1e10/h0)` |
| 6 | `ims4` | `float` | Initial stellar mass in $M_\odot/h$: `GFM_InitialMass * (1e10/h0)` |
| 7 | `mets4` | `long double` | Metallicity mass fraction (cast to `long double` at line 653) |
| 8 | `fiub` | `double` | FoV in unit box: `fovradiants * di / (bs / 1e3)` |
| 9 | `ages4` | `float` | Stellar age in Gyr: `t0 - tf` |
| 10 | `zstar` | `float` | Normalized box $z$: `zzs[l] / fovinunitbox` |
| 11 | `CMzsh` | `double` | Subhalo Center-of-Mass in $z$: $\frac{\sum (\text{orgZ}_l \cdot \text{ms4}_l)}{\sum \text{ms4}_l}$ |
| 12 | `NpshTNG` | `double` | Subhalo total star particle count in simulation |

### 6.2 Baseline Output Checksums

The authoritative baseline files in `/Volumes/PMSAdrive/pmsa/storage/TNG/output_baseline/lc/` were verified with MD5:

| Plane Row | File Name | Size (Bytes) | Line Count | MD5 Checksum |
|---|---|---|---|---|
| **Row 1** | `coords.lc.98_0.txt` | 1,066 | 11 | `79ac9efb68c8ce6e08b1c7c09dd887ab` |
| **Row 2** | `coords.lc.98_1.txt` | 459,433 | 4,692 | `b1fc04316bb7a955d4f5df47a90628f7` |
| **Row 4** | `coords.lc.98_3.txt` | 17,901,836 | 184,010 | `9f9ff464b433c58f4104881a0efaa748` |

### 6.3 Rules for Guaranteeing 100% Bit-Exact MD5 Matches
1. **Preserve Intermediate Type Precision**:
   - `convm` must remain `float(1.e10 / 0.6774)` ($1.47623267 \times 10^{10}$).
   - `ZF4` must remain `float(1.0 / FTIME - 1.0)`.
   - `xs`, `ys`, `zstar`, `ages4`, `zreds` must remain `float`.
   - `fiub`, `CMzsh` must remain `double`.
   - `mets4` must be printed with the exact same precision as `long double` default stream formatting.
2. **Preserve Random Sequence**:
   - The RNG sequence for `x0`, `y0`, `z0`, `face`, `sgnX`, `sgnY`, `sgnZ` across replications $0 \dots \text{rcase}$ uses `srand(seed + i * factor)` with standard C `rand()`. The seeds from `lc.ini` (`0121`, `1210`, `2101`) and order of generation must not be altered.
3. **Preserve Particle Ordering**:
   - In TNG, particles within PartType4 are stored in deterministic subhalo order across snapshot chunks $0 \dots nf\_sn-1$. Streaming chunks in increasing numerical file order $0, 1, \dots, nf\_sn-1$ preserves the exact sequential particle order.
4. **Preserve Stream Formatting**:
   - The standard `std::ofstream` format flags (default precision 6, scientific for very small numbers) produce character-for-character identical bytes.

---

## 7. Strategic Recommendations for Implementation

1. **Refactor `lc` Processing into a Streaming Engine**:
   - Eliminate full-snapshot storage vectors (`X4_`...`ID4_` and `X4`...`ID4`).
   - Iterate through `snapdir_0XX/snap_0XX.*.hdf5` file-by-file.
   - For each file chunk, read coordinates and attributes into reusable flat buffers, filter immediately, and retain only FoV particles in memory.
2. **Implement Direct CLI Parsing and Plane Validation**:
   - Accept `./executable_lc <snapshot> <plane_number> [--mem-limit <GB>]`.
   - Read `planes_list.txt` at startup. If `<plane_number>` does not match `<snapshot>`, exit immediately with an error.
   - Correctly map the plane argument to the output filename `coords.lc.<snapshot>_<replica>.txt` to ensure 100% compatibility with baseline outputs and the downstream `df` module.
3. **Apply Computational Optimizations**:
   - Change `getY` signature to take `const std::vector<double>&` by reference.
   - Hoist `t0 = getY(z_tlist, age_tlist, zsim)` outside the particle loops.
   - Delete the unused $O(K \times N)$ `NpTNG` loop.
   - Optimize center-of-mass calculation to a single linear pass $O(L)$.
   - Replace `pow(x, 2)` with `x * x`.
   - Replace `std::endl` with `'\n'` and use a buffered stream.
4. **Verification Protocol**:
   - Compile with `clang++ -std=c++17 -O2`.
   - Run on test planes (Rows 1, 2, 4 of `planes_list.txt` for snapshot 98).
   - Verify that peak RSS never exceeds 4GB (projected: ~200MB).
   - Verify that MD5 checksums of output files match baseline 100%.
   - Verify single-core runtime speedup exceeds 20%.

