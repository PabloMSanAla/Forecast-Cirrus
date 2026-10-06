# FORECAST Documentation

Welcome to the official documentation for **FORECAST** (*Forward Modeling of Cosmological Hydrodynamical Simulations Mimicking Real Observations*).

```{image} https://img.shields.io/badge/A%26A-677%2C%20A102%20(2023)-blue.svg
:target: https://doi.org/10.1051/0004-6361/202346725
:alt: A&A Publication
```
```{image} https://img.shields.io/badge/arXiv-2305.19166-B31B1B.svg
:target: https://arxiv.org/abs/2305.19166
:alt: arXiv Preprint
```
```{image} https://img.shields.io/badge/C%2B%2B-17-00599C.svg
:alt: C++17 Standard
```
```{image} https://img.shields.io/badge/License-MIT-green.svg
:target: https://github.com/flaminiafortuni/FORECAST/blob/main/LICENSE
:alt: License
```

---

## What is FORECAST?

**FORECAST** is a flexible and high-performance software package designed to bridge the gap between large-scale cosmological hydrodynamical simulations (such as [IllustrisTNG](https://www.tng-project.org/), [EAGLE](https://icc.dur.ac.uk/Eagle/), and [SIMBA](http://simba.roe.ac.uk/)) and real astronomical observations from ground- and space-based telescopes (e.g., *JWST*, *Hubble*, *Roman Space Telescope*, *Euclid*, and *Rubin/LSST*).

### High-Level Pipeline Architecture

The pipeline consists of four serial physics modules executed per lightcone slice (plane), followed by an image rasterization and catalog merging post-processing stage:

```text
flowchart LR
    A["Simulation Snapshot<br>(IllustrisTNG HDF5)"] -->|Geometry & FoV Clipping| B["Module 1: LC<br>(Lightcone Slicing)"]
    B -->|coords.lc.*.txt| C["Module 2: DF<br>(Dust-Free Photometry)"]
    C -->|flux.df.*.txt| D["Module 3: DC<br>(Gas-Traced Dust Extinction)"]
    D -->|flux.dc.*.txt| E["Module 4: IGM<br>(Lyman Continuum & Series)"]
    E -->|flux.igm.*.txt| F["Post-Processing<br>(create_image & galaxy_cat)"]
    F --> G["Final FITS Images<br>& Galaxy Catalogs"]
```

---

## Documentation Contents

```{toctree}
:maxdepth: 2
:caption: 🚀 Getting Started
:numbered:

01_overview/introduction.md
01_overview/quickstart.md
01_overview/installation.md
01_overview/paper_citation.md
```

```{toctree}
:maxdepth: 2
:caption: 🔬 Theoretical Methodology
:numbered:

02_theoretical_methods/lightcone_geometry.md
02_theoretical_methods/stellar_populations.md
02_theoretical_methods/dust_attenuation.md
02_theoretical_methods/igm_absorption.md
02_theoretical_methods/image_generation.md
```

```{toctree}
:maxdepth: 2
:caption: 📦 Pipeline Modules
:numbered:

03_modules/lc_module.md
03_modules/df_module.md
03_modules/dc_module.md
03_modules/igm_module.md
03_modules/postprocessing.md
```

```{toctree}
:maxdepth: 2
:caption: 📊 Data Products & Formats
:numbered:

04_data_products/inputs_specification.md
04_data_products/intermediate_catalogs.md
04_data_products/final_catalogs.md
04_data_products/fits_images.md
```

```{toctree}
:maxdepth: 2
:caption: ⚙️ User & HPC Guide
:numbered:

05_user_guide/configuration_ini.md
05_user_guide/batch_pipeline_runner.md
05_user_guide/memory_management.md
05_user_guide/troubleshooting.md
```

```{toctree}
:maxdepth: 2
:caption: 💻 C++ API Reference
:numbered:

06_api_reference/read_tng_particle.md
06_api_reference/sed_engine.md
06_api_reference/igm_engine.md
06_api_reference/utility_functions.md
```

---

## Citing FORECAST

If you use **FORECAST** in your scientific research, please cite the release paper:

> **Fortuni, F., Merlin, E., Fontana, A., Giocoli, C., Romelli, E., Graziani, L., Santini, P., Castellano, M., Charlot, S., & Chevallard, J. (2023).**  
> *FORECAST: A flexible software to forward model cosmological hydrodynamical simulations mimicking real observations.*  
> Astronomy & Astrophysics, 677, A102.  
> DOI: [10.1051/0004-6361/202346725](https://doi.org/10.1051/0004-6361/202346725) | arXiv: [2305.19166](https://arxiv.org/abs/2305.19166)
