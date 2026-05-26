# Extract FORECAST Data from TNG Snapshots

## Overview

The `extract_forecast_data.py` script processes TNG snapshot and group catalog files to create optimized HDF5 files containing only the data required by the FORECAST lightcone module.

## What it does

1. **Reads** TNG snapshot files (all `snap_XXX.Y.hdf5` files in directory)
2. **Reads** TNG group catalog files (all `fof_subhalo_tab_XXX.Y.hdf5` files in directory)
3. **Extracts** only required particle types and fields:
   - **Gas (PartType0)**: Coordinates, Velocities, Masses, ParticleIDs, SubhaloID
   - **Stars (PartType4)**: Coordinates, Velocities, Masses, ParticleIDs, GFM_StellarFormationTime, SubhaloID
4. **Assigns** subhalo membership IDs from group catalogs
5. **Writes** compressed HDF5 file with only extracted data
6. **Reduces** file size significantly (e.g., 4 GB → 0.5 GB per file)

## Usage

### Command Line:

```bash
python extract_forecast_data.py \
    --snapshot-dir TNG100/snapdir_099 \
    --groupcat-dir TNG100/groups_099 \
    --output-dir TNG100/forecast_data \
    --snapshot-num 99
```

### Within Python:

```python
from extract_forecast_data import TNGDataExtractor

extractor = TNGDataExtractor(
    snapshot_dir='TNG100/snapdir_099',
    groupcat_dir='TNG100/groups_099',
    output_dir='TNG100/forecast_data',
    snapshot_num=99
)

output_file = extractor.extract()
```

## Arguments

- `--snapshot-dir`: Directory containing snapshot files (e.g., `TNG100/snapdir_099/`)
- `--groupcat-dir`: Directory containing group catalog files (e.g., `TNG100/groups_099/`)
- `--output-dir`: Output directory for extracted data
- `--snapshot-num`: Snapshot number (e.g., 99 for z=0)

## Output

Creates a single HDF5 file per snapshot:
```
TNG100/forecast_data/forecast_snap_099.hdf5
```

### File Structure:

```
forecast_snap_099.hdf5
├── Header/                    # Copied from original snapshot
│   ├── BoxSize
│   ├── Redshift
│   ├── Time
│   └── ...
├── PartType0/                 # Gas particles
│   ├── Coordinates           # [N, 3] positions in comoving kpc/h
│   ├── Velocities            # [N, 3] velocities in km/s
│   ├── Masses                # [N] masses in 10^10 Msun/h
│   ├── ParticleIDs           # [N] unique particle IDs
│   └── SubhaloID             # [N] subhalo membership (-1 if unassigned)
└── PartType4/                 # Star particles
    ├── Coordinates           # [N, 3] positions in comoving kpc/h
    ├── Velocities            # [N, 3] velocities in km/s
    ├── Masses                # [N] masses in 10^10 Msun/h
    ├── ParticleIDs           # [N] unique particle IDs
    ├── GFM_StellarFormationTime  # [N] formation scale factor
    └── SubhaloID             # [N] subhalo membership (-1 if unassigned)
```

## Important Notes

### Subhalo Membership

- **Full download required**: To get accurate subhalo IDs, you need **all** snapshot and group catalog files
- **Test mode limitation**: If only file 0 is downloaded (test mode), SubhaloID will be -1 for all particles
- **Unassigned particles**: SubhaloID = -1 indicates particles not belonging to any identified subhalo

### File Sizes

For TNG100-1 at z=0 (snapshot 99):
- **Original**: 448 files × ~4 GB = ~1.8 TB total
- **Extracted**: 1 file × varies (depends on data)
- **Single file (test)**: 4 GB → 0.52 GB (~87% reduction)

## Example Workflow

### 1. Download TNG data (full simulation):
```bash
python download_ilustris.py \
    --api-key YOUR_API_KEY \
    --redshift 0.0 \
    --output-dir ./TNG100
```

### 2. Extract FORECAST data:
```bash
python extract_forecast_data.py \
    --snapshot-dir TNG100/snapdir_099 \
    --groupcat-dir TNG100/groups_099 \
    --output-dir TNG100/forecast_data \
    --snapshot-num 99
```

### 3. Use with FORECAST lc module:
The output file can be used directly with the FORECAST lightcone code. Update `lc.ini` to point to the `forecast_data` directory.

## Processing Multiple Snapshots

To process multiple snapshots, create a bash script:

```bash
#!/bin/bash

for snap in 99 98 97 96 95; do
    echo "Processing snapshot $snap..."
    python extract_forecast_data.py \
        --snapshot-dir TNG100/snapdir_${snap} \
        --groupcat-dir TNG100/groups_${snap} \
        --output-dir TNG100/forecast_data \
        --snapshot-num $snap
done
```

## Requirements

- Python 3.x
- h5py
- numpy
- tqdm (for progress bars)

Install dependencies:
```bash
pip install h5py numpy tqdm
```

## Verification

Check the extracted file:
```bash
python read_hdf5.py TNG100/forecast_data/forecast_snap_099.hdf5
```

This will show:
- ✓ SubhaloID field present in Gas and Stars
- Particle counts
- Available fields
- File structure
