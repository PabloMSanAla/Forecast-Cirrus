# Post-Processing & Mock Observation Tools

The post-processing suite provides specialized C++ and Python utilities to rasterize particle fluxes into scientific FITS images and compile merged galaxy catalogs.

---

## 1. FITS Image Generator (`create_image`)
- **Executable**: `postprocessing/create_image/create_image`
- **Source**: `create_image.cpp`, `functions.cpp`, `image.ini`
- **Function**: Takes particle coordinates and fluxes from `flux.igm` (or `flux.dc`) and maps them onto a regular 2D pixel grid.
- **Output**: Single-plane FITS images with standard astronomical World Coordinate System (WCS) headers (`image.<snap>_<plane>_<filter>.fits`).

---

## 2. Image Stacking (`sum_images.py` / `sum_fits.py`)
- Stacks all per-plane FITS images across the entire lightcone into a single mosaic deep-field FITS image for each filter.

---

## 3. Galaxy Catalog Builder (`galaxy_cat.py` & `merge_cat.py`)
- Groups star particles by subhalo membership ID (`shid`).
- Sums the particle fluxes per filter to compute total integrated galaxy photometry ($m_{\text{AB}}$ and flux in $\mu\text{Jy}$).
- Measures morphological and physical properties: stellar mass ($M_*$), star-formation rate (SFR), mass-weighted stellar age, metallicity, and spatial center of mass.
- Outputs merged galaxy catalogs in ASCII and FITS table formats.
