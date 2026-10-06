# Module 2: Dust-Free Photometry (DF)

The **DF** module computes unattenuated synthetic spectral energy distributions and photometry for all star particles within the lightcone.

---

## Purpose & Overview
- Ingests particle properties (`coords.lc.<snap>_<plane>.txt`) from the LC module.
- Interpolates SSP spectral grids (BC03 or CB16) based on each star particle's birth age $t_*$ and metallicity $Z_*$.
- Applies cosmological k-corrections and luminosity distance redshifting.
- Convolves the unattenuated spectrum with telescope transmission bandpasses (e.g. Roman WFI, JWST NIRCam, Euclid, Rubin/LSST).
- Outputs dust-free fluxes in $\mu\text{Jy}$ to `flux.df.<snap>_<plane>.txt`.

---

## Key Files & Implementation
- **Executable**: `df/executable_df`
- **Main Driver**: `df/main_df.cpp`
- **Spectral Synthesis Engine**: `df/SED.h`, `df/SED.cpp`
- **Utility Functions**: `df/functions.h`, `df/functions.cpp`
- **Configuration**: `df/df.ini`
- **Parallel Runner**: `df/df.sh`

---

## CLI Usage
```bash
./executable_df <snapshot> <plane_number> [memory_ceiling_gb] [-ini <df.ini>]
```

---

## Memory & Performance Optimizations
- **Filter Precomputations (`FilterPrecomp`)**: Pre-integrates wavelength-weighting denominators once per filter, accelerating numerical integrals by $>40\%$.
- **Streaming Batch Processing**: Ingests particles in bounded streaming blocks ($B = 100,000$), keeping peak RSS strictly below $35\text{ MB}$.
