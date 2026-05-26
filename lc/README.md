# LC Module (Lightcone Construction)

## Overview

The **LC (Lightcone Construction)** module is the first step in the FORECAST pipeline. It builds the 3D structure of the lightcone from simulation snapshots and extracts stellar particles within a specified field of view (FoV). This module runs independently for each plane of the lightcone and produces coordinate catalogs needed for subsequent modules.

**Reference:** For full details, see [Fortuni et al. (2023)](https://ui.adsabs.harvard.edu/abs/2023arXiv230519166F/abstract)

---

## Prerequisites

Before running the LC module, ensure you have:

1. **TNG Simulation Data**: Downloaded and organized snapshot files following the structure:
   ```
   /path/to/TNG/
   ├── snapdir_0XX/
   │   └── snap_0XX.*.hdf5 (multiple files per snapshot)
   ├── groups_0XX/
   │   └── fof_subhalo_tab_0XX.*.hdf5
   └── offsets_0XX.hdf5
   ```

2. **Reference Data Files** (located in `../files/`):
   - `redshift_list_TNG.txt` — Snapshot IDs with their redshifts
   - `snaplist_TNG.txt` — Available snapshot numbers (sorted high to low)
   - `timelist_TNG.txt` — Snapshot IDs with redshifts and cosmic times
   - `LCDM-comovingdistTNG.dat` — Comoving distances vs. redshift

3. **Configuration File**: `lc.ini` with all required parameters (see below)

---

## Configuration Parameters (lc.ini)

The `lc.ini` file controls all aspects of lightcone construction. All parameters are read in order; lines starting with `!` are comments.

| Parameter | Value | Description |
|-----------|-------|-------------|
| **BOX_MPC_OVER_h** | `35` | Simulation box size in Mpc/h (comoving) |
| **SOURCE_REDSHIFT** | `0.69` | Maximum redshift of the lightcone (highest redshift plane) |
| **FIELD_OF_VIEW_IN_DEGREES_BY_SIDE** | `1.16` | Field of view side length in degrees (square FoV) |
| **IMAGE_RESOLUTION_IN_ARCSECS** | `0.1` | Pixel resolution in arcseconds |
| **FILE_REDSHIFT_LIST_SNAP_AND_Z** | `../files/redshift_list_TNG.txt` | Path to snapshot redshift mapping file |
| **FILE_SNAPSHOTS_AVAILABLE_SORTED_FROM_Z=0** | `../files/snaplist_TNG.txt` | Path to available snapshots list (high-z first) |
| **FILE_TIMELIST_AVAILABLE_SORTED_FROM_Z=0** | `../files/timelist_TNG.txt` | Path to snapshot cosmic time data |
| **PATH_AND_FILE_NAME_OF_COMOVING_DISTANCES** | `../files/LCDM-comovingdistTNG.dat` | Comoving distance file for cosmology |
| **PATH_WHERE_SNAPHOSTS_ARE_LOCATED** | `/Volumes/T7/storage/TNG/TNG50-2-forecast` | Full path to TNG simulation data |
| **PATH_WHERE_TO_OUTPUT_RESULTS** | `/Volumes/T7/storage/TNG/forecast/lc/` | Output directory for coordinate files |
| **SEED_1_FOR_RANDOMIZATION** | `0121` | Random seed for box center randomization |
| **SEED_2** | `1210` | Random seed for box face selection |
| **SEED_3** | `2101` | Random seed for box orientation signs |
| **SIMULATION** | `TNG` | Simulation name (for reference) |

### Key Parameter Combinations

- **Total Lightcone Distance**: Calculated from `SOURCE_REDSHIFT` using comoving distance file
- **Number of Box Replications**: `ceil(Total_Distance / BOX_MPC_OVER_h)`
- **Image Dimensions**: 
  - True pixels: `ceil(FIELD_OF_VIEW_IN_DEGREES_BY_SIDE * 3600 / IMAGE_RESOLUTION_IN_ARCSECS)`
  - Buffer pixels: ~20% additional pixels around edges
  - Total pixels: `truenpix + bufferpix`

---

## Input File Formats

### redshift_list_TNG.txt
Maps snapshot IDs to their corresponding redshifts.
```
SnapID  Reserved  Redshift
0       0         20.05
1       0         14.99
2       0         11.98
...
```

### snaplist_TNG.txt
Lists snapshot numbers in order (highest redshift first, i.e., lowest snapshot number first).
```
99
98
97
...
0
```

### timelist_TNG.txt
Provides cosmic time data for stellar age calculations.
```
SnapID  Redshift  CosmicAge(Gyr)
0       20.05     0.0001
1       14.99     0.0002
...
```

### LCDM-comovingdistTNG.dat
Cosmological comoving distances (for ΛCDM with TNG parameters).
```
Redshift  ComovingDistance(Mpc/h)  LuminosityDistance(Mpc/h)
0.0       0.0                       0.0
0.01      29.9                      30.2
0.02      59.7                      60.5
...
```

---

## Building the Module

```bash
cd /Users/pmsanch1/code/FORECAST/lc
make clean
make
```

This produces the executable `executable_lc`.

---

## Running the Module

### Single Plane Execution

```bash
cd /Users/pmsanch1/code/FORECAST/lc
./executable_lc <restart_file_prefix> <output_prefix>
```

**Arguments:**
- `<restart_file_prefix>`: Base name for restart file (will append `.d`)
  - Restart file contains the plane number (1-indexed) to process
  - Example: `plane_num` → reads from `plane_num.d`
  
- `<output_prefix>`: Base name for output coordinate files
  - Creates output file: `coords.lc.<snapshot>_<plane>.txt` in output directory

**Example:**
```bash
./executable_lc plane_num plane_num
```

This reads plane number from `plane_num.d` and writes results with prefix `plane_num`.

### Automated Plane-by-Plane Processing

To process all planes, use the provided batch script:

```bash
cd /Users/pmsanch1/code/FORECAST/lc
bash batch_plane_lc.sh
```

**Note: The LC module MUST be run for each plane individually.** Each plane corresponds to a unique combination of:
- Redshift (from lightcone structure)
- Snapshot (from `planes_list.txt`)
- Field of view position (randomized)

---

## Processing Files

### plane_num.d

Simple text file containing a single integer (plane number).

**Example for plane 51:**
```
51
```

This file is updated after each plane completes, allowing restart capability.

### planes_list.txt (Auto-generated)

Describes the complete lightcone structure. Generated automatically on first run.

**Format** (space-separated columns):
```
Plane#  Redshift  NearDist(cMpc/h)  FarDist(cMpc/h)  BoxReplica  SnapshotID  SnapshotZ
1       0.0109    29.91             35.00            0           98          0.01
2       0.0175    35.00             69.64            1           98          0.01
...
51      0.6813    1706.37           1715.00          50          60          0.68
52      0.6813    1706.37           1715.00          50          60          0.68
```

**Columns:**
- **Plane#**: Display plane number (1-indexed)
- **Redshift**: Redshift of plane center
- **NearDist, FarDist**: Comoving distance boundaries in Mpc/h
- **BoxReplica**: Which simulation box replication this plane uses (for tiling)
- **SnapshotID**: TNG snapshot number to read
- **SnapshotZ**: Redshift of the snapshot

---

## Output Files

### Coordinate Catalog: coords.lc.<snapshot>_<plane>.txt

**Format** (tab-separated columns):
```
ID  X(Mpc/h)  Y(Mpc/h)  Redshift  Mass(Msun)  InitialMass(Msun)  Metallicity  -  Age(Gyr)  -  CMz_Subhalo  Npart_Subhalo
```

**Column Details:**

| Column | Type | Description |
|--------|------|-------------|
| ID | int | Particle ID within FoV |
| X, Y | float | Transverse comoving coordinates in Mpc/h |
| Redshift | float | Particle redshift (from distance in simulation) |
| Mass | float | Current stellar mass in M☉ |
| InitialMass | float | Mass at star formation in M☉ |
| Metallicity | float | Metallicity (mass fraction) |
| - | - | Unused column |
| Age | float | Stellar age in Gyr (computed from formation redshift) |
| - | - | Unused column |
| CMz_Subhalo | float | Center-of-mass z-coordinate of parent subhalo |
| Npart_Subhalo | int | Number of particles in parent subhalo (from TNG) |

**Example:**
```
0    100.5    -50.2    0.68    1.2e10    1.5e10    0.02    0    2.3    0    1205.4    45
1    102.1    -48.9    0.681   9.8e9     1.3e10    0.018   0    2.5    0    1206.1    45
...
```

### Console Output

The LC module prints:
- Number of images and buffer pixels
- Available snapshots and redshifts
- Lightcone parameters (cosmology, box size, replications)
- Plane reorganization statistics
- Number of particles at each stage:
  - Total particles in snapshot
  - Particles after filtering
  - Particles in field of view
- Coordinate file path and size
- Execution time

---

## Known Issues & Future Fixes

### ⚠️ Index Off-by-One in Restart Mechanism

**Issue:** The restart file contains **display plane numbers** (1-indexed from `planes_list.txt`), but early versions used these directly as array indices (0-indexed).

**Status:** ✅ FIXED in current version
- Conversion: `array_index = display_plane_number - 1`
- Bounds check added for invalid restart plane numbers

**File:** `main_lc.cpp` line 625-631

### ⚠️ Duplicate Last Plane in planes_list.txt

**Issue:** Under certain conditions, the last plane is written twice to `planes_list.txt`, creating duplicate planes with identical parameters.

**Root Cause:** In `main_lc.cpp` lines 514-544, the code checks if an extra snapshot is needed to complete the lightcone. If the distance condition is true but no new snapshot is found, it still writes the last plane again.

**Manifestation:** Planes 51 and 52 (or similar) appear identical in output.

**Current Workaround:** 
- Manually remove the duplicate line from `planes_list.txt`
- Adjust `plane_num.d` accordingly

**Future Fix Needed:**
Track whether a new snapshot was successfully added before writing the extra plane entry:

```cpp
bool snapshot_added = false;
while(snaplist >> s){
  if(s < bfromsnap[nsnaps-1]){
    // ... add plane ...
    snapshot_added = true;
    nsnaps++;
    snaplist.close();
  }
}
if(snapshot_added){  // Only write if a new snapshot was actually added
  pl++;
  planelist << pl << ...
}
```

**File:** `main_lc.cpp` lines 514-544

---

## Troubleshooting

### Error: "HDF5-DIAG: unable to open file"

**Cause:** 
- TNG snapshot path in `lc.ini` is incorrect or drive is not mounted
- Snapshot files don't exist at specified location

**Solution:**
- Verify `PATH_WHERE_SNAPHOSTS_ARE_LOCATED` in `lc.ini`
- Check that snapshot directory structure matches expected format
- Ensure external drives are mounted

### Error: "snapshot list file does not exist"

**Cause:** One of the reference data files is missing or path is wrong

**Solution:**
- Verify all paths in `lc.ini` point to existing files
- Ensure files are in `../files/` directory

### Restart at plane N reads wrong snapshot

**Cause:** Plane duplication or index mismatch (see Known Issues)

**Solution:**
- Verify `planes_list.txt` doesn't have duplicate lines
- Ensure `plane_num.d` contains correct 1-indexed plane number
- Manually correct and rebuild if needed

---

## Performance Notes

- **Typical runtime per plane:** 1-5 minutes (depends on particle count, FoV, I/O)
- **Memory usage:** ~2-4 GB per plane
- **Output file size:** ~100 KB - 10 MB per plane (depends on particle density)

---

## Citation

If you use this module, please cite:

Fortuni, F., et al. (2023). FORECAST: A Fast Lightcone Simulation. *arXiv:2305.19166*

---

## Contact & Support

For issues, questions, or modifications:
- Original author: Erik Romelli (INAF-OATs)
- Current maintainer: Flaminia Fortuni (flaminia.fortuni@inaf.it)
- Repository: https://github.com/flaminiafortuni/FORECAST
