# Installation & Environment Setup

FORECAST is written in modern **C++17** and relies on high-performance scientific and astronomical libraries.

---

## 1. System Dependencies

### macOS (Apple Silicon / Intel via Homebrew)
Install all required libraries with a single Homebrew command:

```bash
brew install gsl openblas lapack cfitsio ccfits fftw eigen armadillo hdf5 parallel doxygen
```

### Linux (Ubuntu / Debian / CentOS / RHEL)
On Ubuntu/Debian:
```bash
sudo apt-get update
sudo apt-get install -y build-essential libgsl-dev libopenblas-dev liblapack-dev \
    libcfitsio-dev libccfits-dev libfftw3-dev libeigen3-dev libarmadillo-dev \
    libhdf5-dev parallel doxygen
```

---

## 2. Stellar Population Synthesis (SSP) Tables

FORECAST requires single stellar population synthesis spectral grids:
- **BC03** (Bruzual & Charlot 2003): Download from [Bruzual & Charlot official repository](https://www.bruzual.org/bc03/).
- **CB16** (Gutkin, Charlot & Bruzual 2016): Contact the authors or download the precomputed CB16 grids.

Store the tables in your preferred storage path (e.g., `/path/to/bc03/`) and update the `PATH_WHERE_BC03_IS` entry in `df.ini` and `dc.ini`.

---

## 3. Building the Executables

The Makefiles automatically detect Homebrew paths on macOS (`/opt/homebrew` or `/usr/local`) and standard Linux library paths.

```bash
# Build all modules
make -C lc clean && make -C lc
make -C df clean && make -C df
make -C dc clean && make -C dc
make -C igm clean && make -C igm
make -C postprocessing/create_image clean && make -C postprocessing/create_image
```

Each module generates a standalone executable:
- `lc/executable_lc`
- `df/executable_df`
- `dc/executable_dc`
- `igm/executable_igm`
- `postprocessing/create_image/create_image`
