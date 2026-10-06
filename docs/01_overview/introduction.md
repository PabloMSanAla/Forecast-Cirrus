# Introduction & Overview

**FORECAST** (**FO**rward modeling of **RE**alistic **A**stronomical **S**urveys from **C**osmological **T**NG/hydro simulations) is a high-performance C++ software framework designed to transform raw hydrodynamical simulation snapshots into realistic multi-wavelength mock galaxy catalogs and astronomical images.

---

## The Scientific Challenge

Modern astronomical observatories, such as the *James Webb Space Telescope* (JWST), the *Nancy Grace Roman Space Telescope*, *Euclid*, and the *Vera C. Rubin Observatory*, are collecting vast deep-field surveys across cosmological epochs. To interpret these observations, astrophysicists rely on cosmological hydrodynamical simulations (e.g., IllustrisTNG, EAGLE, SIMBA, FIRE).

However, comparing simulations directly with observations is non-trivial because:
1. **Simulation boxes are static Euclidean cubes** at discrete redshifts $z$, whereas real telescopes observe along a continuous backward lightcone $z(t)$.
2. **Dust attenuation is spatially heterogeneous** and strongly dependent on the multi-phase interstellar medium (ISM) and circumstellar birth clouds.
3. **Intergalactic Medium (IGM) absorption** attenuates rest-frame UV flux through stochastic neutral hydrogen clouds along the line of sight.
4. **Telescope optics and detectors** introduce Point Spread Function (PSF) blurring, pixelization, and background Poisson/read noise.

FORECAST solves these challenges by providing a rigorous, physical forward-modeling pipeline.

---

## Core Capabilities

- **Continuous Lightcone Reconstruction**: Slices simulation snapshots into concentric spherical shells, replicating and pseudo-randomly rotating the simulation volume to eliminate artificial periodicity.
- **Single Stellar Population (SSP) Synthesis**: Supports Bruzual & Charlot (2003, `bc03`) and Gutkin, Charlot & Bruzual (2016, `cb16`) spectral synthesis grids with Chabrier and Salpeter Initial Mass Functions (IMF).
- **Physical Multi-Phase Dust Attenuation**: Couples the two-component Charlot & Fall (2000) ISM/birth-cloud prescription with Voronoi gas-cell line-of-sight column density integration ($N_{\text{HI}}$, $Z_{\text{gas}}$) based on Nelson et al. (2019) and Fortuni et al. (2023).
- **Inoue et al. (2014) IGM Absorption**: Incorporates both resonant Lyman series scattering and Lyman continuum photoelectric absorption.
- **High-Performance Streaming Architecture**: Strict single-core RAM ceilings (operates within user-defined limits such as 4 GB, 8 GB, 16 GB), dynamic subhalo chunking, and GNU Parallel execution across thousands of lightcone slices.
- **FITS Image & Mock Catalog Generation**: Rasterizes particle fluxes onto user-defined pixel grids with WCS coordinates and aggregates subhalo properties into unified galaxy catalogs.
