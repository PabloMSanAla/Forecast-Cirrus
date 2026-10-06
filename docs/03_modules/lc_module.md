# Module 1: Lightcone Generator (LC)

The **LC** module handles the spatial and cosmological slicing of simulation snapshots, building the geometry of the lightcone and selecting all particles located inside the field of view.

---

## Purpose & Overview
- Reads stellar (`PartType4`) and gas (`PartType0`) resolution elements from IllustrisTNG HDF5 snapshot chunks.
- Maps subhalo membership using SubFind group catalogs and offset tables.
- Computes comoving distances, cosmological slice boundaries, and rotational replications.
- Projects particles into observer-centered angular coordinates $(\theta_x, \theta_y)$ and cosmological redshift $z_{\text{los}}$.
- Produces the master geometry catalog `planes_list.txt` and per-plane particle catalogs `coords.lc.<snap>_<plane>.txt`.

---

## Key Files & Implementation
- **Executable**: `lc/executable_lc`
- **Main Driver**: `lc/main_lc.cpp`
- **HDF5 Ingestion**: `lc/readTNGParticle.h`, `lc/readTNGParticle.cpp`
- **Utility Functions**: `lc/functions.h`, `lc/functions.cpp`
- **Configuration**: `lc/lc.ini`
- **Parallel Runner**: `lc/lc.sh`

---

## CLI Usage
```bash
./executable_lc <snapshot> <plane_number> [memory_ceiling_gb] [-ini <lc.ini>]
```

### Parameters
- `<snapshot>`: Integer simulation snapshot number (e.g. `98`).
- `<plane_number>`: Plane replica index or 1-based display plane number (e.g. `0`).
- `[memory_ceiling_gb]`: Optional maximum peak RSS in GB (default: `4.0`).
- `[-ini <lc.ini>]`: Optional custom path to `lc.ini`.

---

## Memory & Performance Optimizations
- **Direct 1D Ingestion**: Coordinates are read directly into contiguous 1D buffers, eliminating multi-gigabyte intermediate 3D coordinate matrices.
- **Temporary Binary Spooling**: Selected FoV particles are buffered into a fast binary spool ($B = 100,000$ particles), capping peak RAM below $450\text{ MB}$ even on dense snapshots with 50M+ particles.
