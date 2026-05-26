# TNG Download Script - Usage Guide

## Summary

The `download_ilustris.py` script now downloads **both**:

1. **Snapshot files** (`snapdir_XXX/snap_XXX.Y.hdf5`) - Contains particle data:
   - Positions, velocities, masses
   - Particle IDs
   - Gas and star particle properties

2. **Group catalog files** (`groups_XXX/fof_subhalo_tab_XXX.Y.hdf5`) - Contains subhalo information:
   - Subhalo positions, masses, properties
   - Mapping between particles and subhalos
   - FOF group information

## Usage Examples

### Test Mode (download only first file of each type):
```bash
python download_ilustris.py \
    --api-key YOUR_API_KEY \
    --redshift 0.0 \
    --test
```

### Download Full Snapshot at z=0:
```bash
python download_ilustris.py \
    --api-key YOUR_API_KEY \
    --redshift 0.0
```

### Download Multiple Redshifts:
```bash
python download_ilustris.py \
    --api-key YOUR_API_KEY \
    --redshift 0.0 1.0 2.0 5.0
```

### Skip Group Catalogs (snapshot files only):
```bash
python download_ilustris.py \
    --api-key YOUR_API_KEY \
    --redshift 0.0 \
    --no-groupcat
```

### Use Different Simulation:
```bash
python download_ilustris.py \
    --api-key YOUR_API_KEY \
    --simulation TNG100-3 \
    --redshift 0.0 \
    --test
```

## Downloaded File Structure

```
TNG100/
├── snapdir_099/           # Snapshot files
│   ├── snap_099.0.hdf5    # ~4 GB (test: 1 file, full: 448 files)
│   ├── snap_099.1.hdf5
│   └── ...
└── groups_099/            # Group catalog files
    ├── fof_subhalo_tab_099.0.hdf5   # ~11 MB (test: 1 file, full: 448 files)
    ├── fof_subhalo_tab_099.1.hdf5
    └── ...
```

## File Sizes (TNG100-1 at z=0)

- **Snapshot files**: ~1.8 TB total (448 files × ~4 GB each)
- **Group catalog files**: ~4.4 GB total (448 files × ~10 MB each)
- **Test mode**: Downloads only first file of each (~4 GB + ~11 MB)

## Group Catalog Contents

The `fof_subhalo_tab_XXX.Y.hdf5` files contain:

### Subhalo Group:
- `SubhaloPos` - Position of each subhalo
- `SubhaloMass` - Total mass
- `SubhaloLen` - Number of particles in subhalo
- `SubhaloLenType` - Number of particles by type (gas, DM, stars, etc.)
- `SubhaloVel` - Velocity
- Many more properties...

### IDs Group (for linking particles to subhalos):
- Particle IDs sorted by subhalo membership
- Use `SubhaloLen` to determine which particles belong to which subhalo

## Linking Particles to Subhalos

To find which subhalo a particle belongs to:

1. Read particle IDs from snapshot file
2. Read particle IDs from group catalog (sorted by subhalo)
3. Use `SubhaloLen` array to map ID ranges to subhalo numbers

Alternatively, use the offset arrays in the group catalog to directly access particles by subhalo.

## Configuration for FORECAST lc Module

The downloaded files match the TNG format expected by the FORECAST lightcone code:

- Snapshots in `snapdir_XXX/` folders
- Group catalogs in `groups_XXX/` folders  
- Standard TNG HDF5 structure
- Compatible with `readTNGParticle.cpp` in the lc module

## Tips

- **Use TNG100-3 for testing**: 8× fewer particles, much faster downloads
- **Test mode first**: Always test with `--test` before full download
- **Resume capability**: Script skips already downloaded files
- **API key**: Get yours from https://www.tng-project.org/users/profile/
