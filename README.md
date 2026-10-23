# FORECAST

**FORECAST** (*FOrward modeling hydrodynamical REsolutions into Cost-effective Astronomical Synthetic surveys and Targets*) is a high-performance, modular pipeline designed to construct realistic mock astronomical lightcones, galaxy catalogs, and synthetic astronomical images (FITS) from hydrodynamical cosmological simulations (e.g., IllustrisTNG).

---

## Table of Contents
1. [Key Features & Hardware Requirements](#key-features--hardware-requirements)
2. [Installation](#installation)
3. [Configuration (`forecast.yaml`)](#configuration-forecastyaml)
4. [Unified CLI Usage (`forecast`)](#unified-cli-usage-forecast)
5. [Module-by-Module Reference](#module-by-module-reference)
6. [Parallel Batch Execution (GNU Parallel)](#parallel-batch-execution-gnu-parallel)
7. [Python Postprocessing Library](#python-postprocessing-library)
8. [Exit Codes](#exit-codes)
9. [Citation](#citation)

---

## Key Features & Hardware Requirements

### Low-RAM Friendly & RAM-Aware Execution
All modules in FORECAST include **active RSS memory ceiling monitoring** and **streaming architectures**:
- **Runs on Consumer Laptops / Local Machines**: The entire pipeline can execute safely within user-defined memory limits (e.g., **4 GB**, **8 GB**, or **16 GB** RAM limits).
- **Zero OOM Crashes**: If an individual process approaches the memory limit, it gracefully exits with code `3` rather than triggering an operating system kernel kill (`SIGKILL`/OOM).
- **Streaming Algorithms**:
  - `lc`: Bounded binary spooling and online subhalo aggregators cap peak RAM below **420 MB** (even on 110M+ particle slices).
  - `df`: Bounded batch streaming caps peak RAM under **35 MB**.
  - `dc` & `igm`: Two-pass streaming catalog ingestion bounds peak RAM under **350 MB** (even with 50M+ stars and 140M+ gas cells).
  - `create_image`: Automatically sizes horizontal row slabs to fit within your designated RAM budget (e.g. 4 GB ceiling = 3 slabs, 16 GB ceiling = 1 single pass).

### Hardware Requirements
| Resource | Minimum (Budget Laptop) | Recommended (Workstation / HPC) |
| :--- | :--- | :--- |
| **RAM** | **4 GB** (using `-m 4.0`) | **16 GB – 32 GB** |
| **CPU** | 2 cores (serial execution) | 8–32+ cores for GNU Parallel batch runs |
| **Storage** | 100 GB+ free disk space | Fast NVMe SSD (recommended for fast FITS writing) |
| **OS** | Linux (x86_64) or macOS (Apple Silicon / Intel) | Linux (x86_64) |

---

## Installation

FORECAST uses a pure **Conda** toolchain and compiles natively on both **Linux** and **macOS** (Apple Silicon `arm64` and Intel `x86_64`) without requiring Homebrew or system-level root packages.

### 1. Create and Activate the Conda Environment
```bash
git clone https://github.com/flaminiafortuni/FORECAST.git
cd FORECAST

# Create environment with all C++ and Python dependencies
conda env create -f environment.yml
conda activate forecast
```

### 2. Build and Install
Compile all C++ modules, link CLI binaries into `$CONDA_PREFIX/bin`, and install the Python package:
```bash
make all
make install
```

Verify the installation:
```bash
forecast check
```

*(To run automated tests and verify MD5 determinism: `make test`)*

---

## Configuration (`forecast.yaml`)

FORECAST is configured through a unified YAML configuration file: `forecast.yaml`.

```yaml
geometry:
  box_size: 35.0                    # Simulation box size in Mpc/h
  field_of_view_deg: 1.16           # FOV side in degrees
  source_redshift: 0.7              # Maximum lightcone redshift
  image_resolution_arcsec: 0.1      # Pixel scale in arcsec/pixel
  planes_list_file: "lc/planes_list.txt"

simulation:
  snapshot_dir: "/path/to/TNG50-2/" # Directory containing snapdir_XXX/
  subhalo_dir: "/path/to/TNG50-2/"

modules:
  ssp_model: "bc03"                 # bc03 or cb16
  imf: "chabrier"                   # chabrier or salpeter
  filter_name: "Roman_WFI_f158"     # Target filter for images
  filters_file: "files/filters.dat"
  extinction_file: "dc/extinctionCCM89.dat"

paths:
  output_dir: "output/"             # Base output directory
  memory_ceiling_gb: 4.0            # Memory limit per process in GB
```

*(Legacy `.ini` files—`lc.ini`, `df.ini`, `dc.ini`, `igm.ini`, `image.ini`—remain fully supported).*

---

## Unified CLI Usage (`forecast`)

The `forecast` command-line tool provides a unified entry point for inspecting, running, and managing every stage of the pipeline.

```bash
# Validate environment, compilers, and configuration paths
forecast check [-c forecast.yaml]

# Display or filter planes list
forecast planes [-c forecast.yaml]

# Run a single plane for a specific module
forecast <lc|df|dc|igm|image> <snapshot> <plane> [memory_ceiling_gb] [-c forecast.yaml]

# Run a full module batch in parallel across all planes
forecast <lc|df|dc|igm|image> -c forecast.yaml -n 4 -m 4.0

# Run the complete end-to-end pipeline across all planes
forecast run -c forecast.yaml -n 4 -m 4.0

# Stack plane FITS images into a final lightcone mosaic
forecast stack -c forecast.yaml
```

---

## Module-by-Module Reference

Each module can also be invoked directly as a standalone executable.

### 1. `lc` (Lightcone Construction)
Reads stellar and gas particles from simulation HDF5 snapshots and selects elements within the lightcone geometry.
* **CLI Executable**:
  ```bash
  ./lc/executable_lc <snapshot> <plane> [memory_ceiling_gb] [-c forecast.yaml | -ini lc/lc.ini]
  ```
* **Example**:
  ```bash
  ./lc/executable_lc 98 0 4.0 -c forecast.yaml
  ```
* **Output**: `coords.lc.<snapshot>_<plane>.txt` (ASCII particle coordinates and properties).

---

### 2. `df` (Dust-Free Photometry)
Computes synthetic SEDs, k-corrections, and dust-free fluxes across selected filters using BC03 or CB16 SSP models.
* **CLI Executable**:
  ```bash
  ./df/executable_df <snapshot> <plane> [memory_ceiling_gb] [-c forecast.yaml | -ini df/df.ini]
  ```
* **Example**:
  ```bash
  ./df/executable_df 98 0 4.0 -c forecast.yaml
  ```
* **Output**: `flux.df.<snapshot>_<plane>.txt` (stellar particles with dust-free fluxes).

---

### 3. `dc` (Dust Attenuation)
Extracts gas cell column densities and metallicities from simulation snapshots to compute dust optical depth and attenuated fluxes.
* **CLI Executable**:
  ```bash
  ./dc/executable_dc <snapshot> <plane> [memory_ceiling_gb] [-c forecast.yaml | -ini dc/dc.ini]
  ```
* **Example**:
  ```bash
  ./dc/executable_dc 98 0 4.0 -c forecast.yaml
  ```
* **Outputs**: `flux.dc.<snapshot>_<plane>.txt`, `coords.dc.<snapshot>_<plane>.txt`.

---

### 4. `igm` (Intergalactic Medium Absorption)
Applies IGM transmission corrections (Inoue et al. 2014) to dust-attenuated fluxes as a function of redshift and wavelength.
* **CLI Executable**:
  ```bash
  ./igm/executable_igm <snapshot> <plane> [memory_ceiling_gb] [-c forecast.yaml | -ini igm/igm.ini]
  ```
* **Example**:
  ```bash
  ./igm/executable_igm 98 0 4.0 -c forecast.yaml
  ```
* **Output**: `flux.igm.<snapshot>_<plane>.txt`.

---

### 5. `create_image` (FITS Rasterization)
Projects 3D particle positions and fluxes onto a 2D pixel grid, dynamically streaming horizontal row slabs to enforce RAM limits, and outputs a 16-bit floating-point FITS image.
* **CLI Executable**:
  ```bash
  ./postprocessing/create_image/executable_create_image <snapshot> <plane> [memory_ceiling_gb] [-c forecast.yaml | -ini postprocessing/create_image/image.ini]
  ```
* **Example**:
  ```bash
  ./postprocessing/create_image/executable_create_image 98 0 4.0 -c forecast.yaml
  ```
* **Output**: `<filter>.<module>.<snapshot>_<plane>.fits`.

---

## Parallel Batch Execution (GNU Parallel)

All modules include robust batch runner scripts powered by **GNU Parallel**. Each script automatically validates inputs, enforces per-job memory ceilings, logs execution details, and **skips already completed planes** for seamless restartability.

```bash
# Lightcone module
./lc/lc.sh -c forecast.yaml -n 4 -m 4.0

# Dust-Free module
./df/df.sh -c forecast.yaml -n 4 -m 4.0

# Dust-Corrected module
./dc/dc.sh -c forecast.yaml -n 4 -m 4.0

# IGM module
./igm/igm.sh -c forecast.yaml -n 4 -m 4.0

# Image generation module
./postprocessing/create_image/im.sh -c forecast.yaml -n 4 -m 4.0

# Full end-to-end pipeline batch runner
./forecast.sh -c forecast.yaml -n 4 -m 4.0
```

### Common Batch Script Options
| Flag | Description | Default |
| :--- | :--- | :--- |
| `-n <cores>` | Number of parallel jobs | Number of CPU cores |
| `-m <GB>` | Memory ceiling per job in GB | `4.0` |
| `-c <path>` | Path to unified `forecast.yaml` | `forecast.yaml` |
| `-max <N>` | Process only up to plane index `N` | All planes in `planes_list.txt` |
| `-f, --force` | Force recomputation, overwriting existing outputs | Off (skips existing non-empty files) |
| `-j <log>` | GNU parallel job log file path | None |
| `-r <dir>` | Directory to save per-plane stdout and stderr | None |

---

## Python Postprocessing Library

The `forecast` package provides Python utilities for catalog aggregation and FITS stacking:

```python
from forecast.postprocessing import (
    build_galaxy_catalog,
    merge_galaxy_catalogs,
    stack_fits_images,
)

# 1. Convert particle tables into galaxy-level mock catalogs
build_galaxy_catalog(
    planes_file="lc/planes_list.txt",
    module="igm",
    input_path="output/igm/",
    filter_pos=0,
    fov_deg=1.16,
    res_as=0.1
)

# 2. Merge all plane catalogs into a final lightcone galaxy catalog
merge_galaxy_catalogs(
    planes_file="lc/planes_list.txt",
    module="igm",
    input_path="output/igm/",
    output_catalog="output/final_cat.igm.dat"
)

# 3. Stack per-plane FITS images into a deep mock survey image
stack_fits_images(
    image_dir="output/image/",
    filter_name="Roman_WFI_f158",
    module="igm",
    output_fits="output/stacked_mosaic.fits"
)
```

---

## Exit Codes

All executables adhere to standard exit codes:
* `0`: **Success** — Job completed and verified.
* `1`: **Input / Validation Error** — Missing arguments, invalid numbers, or `(snapshot, plane)` pair not found in `planes_list.txt`.
* `2`: **File / I/O Error** — Missing input files, unreadable HDF5 dataset, or missing configuration file.
* `3`: **Memory Ceiling Breach** — Process exceeded the user-specified RAM limit (`--mem`).

---

## Citation

If you use FORECAST in your research, please cite:

```bibtex
@ARTICLE{2023A&A...677A.102F,
       author = {{Fortuni}, Flaminia and {Merlin}, Emiliano and {Fontana}, Adriano and {Giocoli}, Carlo and {Romelli}, Erik and {Graziani}, Luca and {Santini}, Paola and {Castellano}, Marco and {Charlot}, St{\'e}phane and {Chevallard}, Jacopo},
        title = "{FORECAST: A flexible software to forward model cosmological hydrodynamical simulations mimicking real observations}",
      journal = {\aap},
         year = 2023,
        month = sep,
       volume = {677},
          eid = {A102},
        pages = {A102},
          doi = {10.1051/0004-6361/202346725}
}
```
