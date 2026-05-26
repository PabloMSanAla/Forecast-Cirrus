# Complete FORECAST TNG Data Processing Pipeline

This directory contains a complete pipeline for downloading, extracting, and preparing TNG simulation data for the FORECAST lightcone module.

## Scripts Overview

| Script | Purpose | Input | Output |
|--------|---------|-------|--------|
| `download_ilustris.py` | Download TNG snapshots and group catalogs | API key, redshift | Raw TNG HDF5 files |
| `extract_forecast_data.py` | Extract required fields only | Raw TNG files | Optimized HDF5 files |
| `batch_extract.py` | Process multiple snapshots | Multiple snapshots | Multiple optimized files |
| `verify_forecast_data.py` | Validate extracted data | Extracted files | Validation report |
| `read_hdf5.py` | Inspect HDF5 file structure | Any HDF5 file | Structure report |

## Complete Workflow

### Step 1: Download TNG Data

Download snapshot and group catalog files from IllustrisTNG:

```bash
# Test mode (1 file each, ~4 GB)
python download_ilustris.py \
    --api-key YOUR_API_KEY \
    --redshift 0.0 \
    --test \
    --output-dir ./TNG100

# Full download (all files, ~1.8 TB for TNG100-1 at z=0)
python download_ilustris.py \
    --api-key YOUR_API_KEY \
    --redshift 0.0 \
    --output-dir ./TNG100
```

**Output structure:**
```
TNG100/
├── snapdir_099/              # Snapshot files (particle data)
│   ├── snap_099.0.hdf5      # ~4 GB each
│   ├── snap_099.1.hdf5
│   └── ... (448 files total for TNG100-1)
└── groups_099/               # Group catalogs (subhalo info)
    ├── fof_subhalo_tab_099.0.hdf5  # ~11 MB each
    ├── fof_subhalo_tab_099.1.hdf5
    └── ... (448 files total)
```

### Step 2: Extract FORECAST Data

Process downloaded files to extract only required fields:

```bash
# Single snapshot
python extract_forecast_data.py \
    --snapshot-dir TNG100/snapdir_099 \
    --groupcat-dir TNG100/groups_099 \
    --output-dir TNG100/forecast_data \
    --snapshot-num 99

# Multiple snapshots (batch processing)
python batch_extract.py \
    --base-dir TNG100 \
    --snapshots 99 98 97 96 95 \
    --output-dir TNG100/forecast_data
```

**Output:**
```
TNG100/forecast_data/
├── forecast_snap_099.hdf5    # Extracted data (~0.5 GB)
├── forecast_snap_098.hdf5
└── ...
```

**Size reduction**: ~87% (4 GB → 0.5 GB per file) by:
- Keeping only Gas and Stars (removing DM, BH)
- Keeping only required fields
- Using compression

### Step 3: Verify Data

Validate that extracted files are correctly formatted:

```bash
# Single file
python verify_forecast_data.py TNG100/forecast_data/forecast_snap_099.hdf5

# Multiple files
python verify_forecast_data.py TNG100/forecast_data/*.hdf5
```

### Step 4: Configure FORECAST

Update `lc/lc.ini` to point to extracted data:

```ini
!...PATH_WHERE_SNAPHOSTS_ARE_LOCATED
../TNG100/forecast_data/
```

## Data Format

### Extracted HDF5 File Structure

```
forecast_snap_XXX.hdf5
├── Header/                       # Simulation metadata
│   ├── BoxSize                   # Box size in kpc/h
│   ├── Redshift                  # Snapshot redshift
│   ├── Time                      # Scale factor
│   ├── HubbleParam               # H0/100
│   └── ...
├── PartType0/                    # GAS PARTICLES
│   ├── Coordinates              # [N, 3] float32 - Position (comoving kpc/h)
│   ├── Velocities               # [N, 3] float32 - Velocity (km/s)
│   ├── Masses                   # [N] float32 - Mass (10^10 Msun/h)
│   ├── ParticleIDs              # [N] uint64 - Unique particle ID
│   └── SubhaloID                # [N] int32 - Subhalo membership (-1 if unassigned)
└── PartType4/                    # STAR PARTICLES
    ├── Coordinates              # [N, 3] float32 - Position (comoving kpc/h)
    ├── Velocities               # [N, 3] float32 - Velocity (km/s)
    ├── Masses                   # [N] float32 - Mass (10^10 Msun/h)
    ├── ParticleIDs              # [N] uint64 - Unique particle ID
    ├── GFM_StellarFormationTime # [N] float32 - Formation scale factor
    └── SubhaloID                # [N] int32 - Subhalo membership (-1 if unassigned)
```

## Important Notes

### Subhalo Assignment

- **Requires full download**: SubhaloID assignment needs **all** group catalog files
- **Test mode limitation**: With only 1 file downloaded, SubhaloID = -1 for all particles
- **Still valid**: Files without subhalo IDs are still compatible with FORECAST

### File Sizes

#### TNG100-1 at z=0:
- **Raw download**: 448 files × 4 GB = ~1.8 TB snapshots + 4.4 GB group catalogs
- **Extracted**: 1 file × varies (typically 0.5-1 GB per original file)
- **Total reduction**: ~10× smaller

#### TNG100-3 (recommended for testing):
- **Raw download**: 8× fewer particles than TNG100-1
- **Much faster**: Downloads and processing

## Quick Start Examples

### Minimal Test (Fast)
```bash
# Download 1 file (~4 GB)
python download_ilustris.py \
    --api-key YOUR_KEY \
    --simulation TNG100-3 \
    --redshift 0.0 --test

# Extract (~5 seconds)
python extract_forecast_data.py \
    --snapshot-dir TNG100/snapdir_099 \
    --groupcat-dir TNG100/groups_099 \
    --output-dir TNG100/forecast_data \
    --snapshot-num 99

# Verify
python verify_forecast_data.py TNG100/forecast_data/forecast_snap_099.hdf5
```

### Full Production Run
```bash
# Download all snapshots needed
for z in 0.0 1.0 2.0 5.0 10.0; do
    python download_ilustris.py \
        --api-key YOUR_KEY \
        --redshift $z \
        --output-dir ./TNG100
done

# Extract all
python batch_extract.py \
    --base-dir TNG100 \
    --snapshots 99 84 78 58 40 \
    --output-dir TNG100/forecast_data

# Verify all
python verify_forecast_data.py TNG100/forecast_data/*.hdf5
```

## Error Handling

### Common Issues

1. **"No snapshot files found"**
   - Check `--snapshot-dir` path is correct
   - Ensure files were downloaded successfully

2. **"No group catalog files found"**
   - Non-fatal: extraction continues without subhalo IDs
   - Files are still valid for FORECAST

3. **"Gas/Star particles mapped: 0"**
   - Expected in test mode (only 1 file downloaded)
   - Need all files for complete subhalo mapping

4. **Large file sizes**
   - TNG100-1 is very large (~1.8 TB per snapshot)
   - Consider TNG100-3 for testing (8× smaller)

## Performance Tips

1. **Use TNG100-3 for development/testing**
2. **Download with `--test` first** to verify everything works
3. **Process multiple snapshots with `batch_extract.py`**
4. **Verify files immediately after extraction**
5. **Keep original downloads** in case re-extraction is needed

## Requirements

```bash
pip install h5py numpy tqdm requests
```

## Getting API Key

1. Register at: https://www.tng-project.org/users/register/
2. Login and visit: https://www.tng-project.org/users/profile/
3. Copy your API key

## Questions/Issues

For TNG data questions: https://www.tng-project.org/
For FORECAST questions: See FORECAST repository documentation
