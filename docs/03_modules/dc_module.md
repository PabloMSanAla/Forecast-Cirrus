# Module 3: Dust Correction (DC)

The **DC** module computes spatially resolved dust attenuation by coupling the two-phase stellar birth-cloud model with line-of-sight gas column densities and metallicities extracted directly from the cosmological simulation.

---

## Purpose & Overview
- Reads dust-free fluxes (`flux.df.<snap>_<plane>.txt`) and aggregates subhalo properties online.
- Ingests simulation gas cells (`PartType0`) across HDF5 snapshot chunks to measure column density $N_{\text{HI}}$ and gas metallicity $\langle Z_{\text{gas}} \rangle$ in front of star particles.
- Applies the Cardelli, Clayton & Mathis (1989, CCM89) Milky Way extinction curve and Nelson et al. (2019) / Fortuni et al. (2023) optical depth scaling.
- Evaluates dust-attenuated apparent magnitudes and reddening correction ratios $d_{f, i} = f_{\text{dc}, i} / f_{\text{df}, i}$.
- Produces reddened particle catalogs `flux.dc.<snap>_<plane>.txt` and gas property catalog `coords.dc.<snap>_<plane>.txt`.

---

## Key Files & Implementation
- **Executable**: `dc/executable_dc`
- **Main Driver**: `dc/main_dc.cpp`
- **Extinction Curve**: `dc/extinctionCCM89.dat`
- **HDF5 Gas Ingestion**: `dc/readTNGParticle.h`, `dc/readTNGParticle.cpp`
- **Spectral Engine**: `dc/SED.h`, `dc/SED.cpp`
- **Configuration**: `dc/dc.ini`
- **Parallel Runner**: `dc/dc.sh`

---

## Dynamic Subhalo Chunking Architecture
To prevent Out-Of-Memory crashes on dense simulation planes with $40\text{M}+$ stars and $100\text{M}+$ gas cells across $50,000+$ galaxies:
- **Pass 1**: Aggregates lightweight subhalo scalar properties ($< 10\text{ MB}$ RAM).
- **Dynamic Chunking**: Automatically sizes spectrum batch buffers to fit the available RAM ceiling (`-m` flag).
- **Batch Processing**: Allocates SED spectra only for the active chunk of subhalos, computes filter fluxes, and frees the buffer before advancing to the next chunk.
