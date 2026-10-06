# Configuration Files (.ini) Reference

FORECAST parameterizes simulation runs through structured `.ini` files.

---

## 1. Parameters Specification

### `lc.ini` (Lightcone Module)
```ini
!...BOX_MPC_OVER_h
35                               # Simulation box side length in Mpc/h (e.g. 35 for TNG50)
!...REDSHIFT_OF_SOURCES
2.9                              # Maximum source redshift (zs)
!...FOV_IN_DEGREES
0.14                             # Square field of view side length in degrees
!...FILE_SNAPSHOTS_AVAILABLE_SORTED_FROM_Z=0
/path/to/snaplist_TNG.txt        # Snapshot list ordered from z=0
!...FILE_TIMELIST_AVAILABLE_SORTED_FROM_Z=0
/path/to/timelist_TNG.txt        # Time/redshift lookup table
!..PATH_AND_FILE_NAME_OF_COMOVING_DISTANCES
/path/to/LCDM-comovingdistTNG.dat # Cosmology lookups
!...PATH_WHERE_SNAPHOSTS_ARE_LOCATED
/path/to/TNG50-2/                # Root directory containing snapdir_* and groups_*
!...PATH_WHERE_TO_OUTPUT_RESULTS
/path/to/forecast/lc/            # Directory where coords.lc.*.txt will be saved
!...PLANES_LIST_FILE
/path/to/planes_list.txt         # Path where planes_list.txt will be generated
```

### `df.ini` (Dust-Free Photometry Module)
```ini
!...FILTERS_FILE
/path/to/files/filters.dat       # List of filter names
!...PATH_WHERE_BC03_IS
/path/to/bc03/                   # Root directory containing BC03/CB16 spectral tables
!...PATH_WHERE_LC_CATALOGS
/path/to/forecast/lc/            # Path containing coords.lc.*.txt
!...PATH_WHERE_TO_OUTPUT_RESULTS
/path/to/forecast/df/            # Path where flux.df.*.txt will be saved
!...SSP_MODEL_bc03_OR_cb16
bc03                             # Stellar model: bc03 or cb16
!...IMF_chabrier_OR_salpeter
chabrier                         # IMF: chabrier or salpeter
```

### `dc.ini` (Dust Correction Module)
```ini
!...MAG_LIM_(i=0_of_filter_list)
33.5                             # Limiting magnitude for dust processing
!...EXTINCTION_FILE
/path/to/dc/extinctionCCM89.dat  # Extinction curve file
!...READ_GAS_FROM_CATALOG(=0)_OR_FROM_SCRATCH(=1)
1                                # 1: Read HDF5 gas cells, 0: Read precomputed coords.dc
```

### `igm.ini` (IGM Module)
```ini
!...PATH_WHERE_DC_CATALOGS
/path/to/forecast/dc/            # Directory containing flux.dc.*.txt
!...PATH_WHERE_TO_OUTPUT_RESULTS
/path/to/forecast/igm/           # Directory where flux.igm.*.txt will be saved
```
