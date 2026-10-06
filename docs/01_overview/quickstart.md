# Quickstart Guide

This guide walks you through running your first FORECAST pipeline execution for a single lightcone plane.

---

## 1. Prerequisites & Compilation

Ensure all required libraries are installed (see [Installation Guide](installation.md)). Compile all four C++ modules:

```bash
# Clone the repository
git clone https://github.com/flaminiafortuni/FORECAST.git
cd FORECAST

# Compile all modules
make -C lc
make -C df
make -C dc
make -C igm
make -C postprocessing/create_image
```

Each module produces an executable (`executable_lc`, `executable_df`, `executable_dc`, `executable_igm`).

---

## 2. Setting Up Configuration Files

FORECAST uses standard `.ini` configuration files. Ensure `lc.ini`, `df.ini`, `dc.ini`, and `igm.ini` point to your simulation snapshots and desired output directories:

```ini
!...BOX_MPC_OVER_h
35
!...PATH_WHERE_SNAPHOSTS_ARE_LOCATED
/path/to/TNG50-2/
!...PATH_WHERE_TO_OUTPUT_RESULTS
/path/to/outputs/
```

---

## 3. Running a Single Plane Manually

Each module accepts `<snapshot> <plane_number> [memory_ceiling_gb] [-ini <config.ini>]`.

For example, to process **Snapshot 98, Plane 0** under a strict **4.0 GB memory ceiling**:

```bash
# Step 1: Lightcone Geometry & Particle Slicing
./lc/executable_lc 98 0 4.0 -ini lc/lc.ini

# Step 2: Dust-Free Photometry Calculation
./df/executable_df 98 0 4.0 -ini df/df.ini

# Step 3: Gas-Traced Dust Attenuation
./dc/executable_dc 98 0 4.0 -ini dc/dc.ini

# Step 4: Intergalactic Medium Absorption
./igm/executable_igm 98 0 4.0 -ini igm/igm.ini
```

---

## 4. Running the Entire Pipeline in Parallel with `forecast.sh`

To process multiple planes in parallel across 16 CPU cores with GNU Parallel:

```bash
./forecast.sh -n 16 -i 0 -max 30 -m 4.0 -ini-dir /path/to/configs -j forecast_jobs.log -r logs/
```

### CLI Options Summary
- `-n 16`: Use 16 parallel CPU workers.
- `-i 0`: Start at plane 0.
- `-max 30`: Stop after plane 30.
- `-m 4.0`: Enforce 4.0 GB maximum RAM per worker.
- `-ini-dir /path/to/configs`: Directory containing all `.ini` files.
- `-j forecast_jobs.log`: Record runtime and exit status logs for all planes.
- `-r logs/`: Store standard output and error streams for each plane.

---

## 5. Generating FITS Images and Catalogs

After the particle catalogs (`flux.igm.<snap>_<plane>.txt`) are generated:

```bash
# Create FITS images for each plane and filter
cd postprocessing/create_image
./create_image 98 0

# Merge into a final mock galaxy catalog
cd ..
python3 galaxy_cat.py /path/to/igm_catalogs/
```
