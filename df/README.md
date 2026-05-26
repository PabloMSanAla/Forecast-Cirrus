# DF Module (Dust-Free Flux Calculations)

## Overview

The **DF (Dust-Free Fluxes)** module is the second step in the FORECAST pipeline. It computes dust-free apparent magnitudes and fluxes for all stellar particles in the lightcone using stellar population synthesis (SPS) models. This module:

- Reads particle catalogs created by the **LC module**
- Computes spectral energy distributions (SEDs) using BC03 or CB16 stellar models
- Applies k-corrections for redshift evolution
- Calculates dust-free fluxes in multiple photometric filters
- Outputs catalog with per-particle fluxes needed for subsequent modules

**Reference:** For full details, see [Fortuni et al. (2023)](https://ui.adsabs.harvard.edu/abs/2023arXiv230519166F/abstract)

---

## Prerequisites

Before running the DF module, ensure you have:

1. **LC Module Output**: Coordinate catalogs (`coords.lc.*.txt`) from the LC module for each plane
2. **Planes List**: `planes_list.txt` created by LC module
3. **BC03 or CB16 Stellar Models**: Directory containing SPS model spectra
   - BC03 (Bruzual & Charlot 2003): 1221 wavelength points
   - CB16 (Conroy & van Dokkum 2012 updated to 2016): 13,391 wavelength points
4. **Filter Data**: Individual filter response files in subdirectories under filters/
5. **Reference Data Files**: Same as LC module (redshift lists, timelist, comoving distances)
6. **Configuration File**: `df.ini` with all required parameters

---

## Configuration Parameters (df.ini)

The `df.ini` file controls SPS model parameters and computation settings. All parameters are read in order; lines starting with `!` are comments.

| Parameter | Example | Description |
|-----------|---------|-------------|
| **BOX_MPC_OVER_h** | `35` | Simulation box size in Mpc/h (must match LC module) |
| **SOURCE_REDSHIFT** | `0.69` | Maximum redshift of lightcone (must match LC module) |
| **FILTERS_FILE** | `../files/filters.dat` | Path to filter names list |
| **FILE_REDSHIFT_LIST_SNAP_A_AND_Z** | `../files/redshift_list_TNG.txt` | Snapshot ID to redshift mapping |
| **FILE_SNAPSHOTS_AVAILABLE_SORTED_FROM_Z=0** | `../files/snaplist_TNG.txt` | Available snapshots list |
| **FILE_TIMELIST_AVAILABLE_SORTED_FROM_Z=0** | `../files/timelist_TNG.txt` | Snapshot cosmic time data |
| **PATH_AND_FILE_NAME_OF_COMOVING_DISTANCES** | `../files/LCDM-comovingdistTNG.dat` | Comoving distance file |
| **PATH_WHERE_SNAPHOSTS_ARE_LOCATED** | `/Volumes/T7/.../TNG50-2-forecast` | Path to TNG snapshot data (must match LC) |
| **PATH_WHERE_BC03_IS** | `../../bc03` | Directory containing BC03/CB16 SPS models |
| **PATH_WHERE_TO_OUTPUT_RESULTS** | `./` | Output directory for flux catalogs |
| **MODEL_bc03_or_cb16** | `cb16` | SPS model: `bc03` or `cb16` |
| **IMF_chabrier_or_salpeter** | `chabrier` | Initial mass function: `chabrier` or `salpeter` |

### Key Parameters Explained

- **MODEL**: Determines stellar population synthesis model
  - `bc03`: Lower resolution (1221 wavelengths), faster
  - `cb16`: Higher resolution (13,391 wavelengths), more accurate
  
- **IMF**: Initial mass function for stellar mass determinations
  - `chabrier`: Modern Chabrier IMF (recommended)
  - `salpeter`: Classic Salpeter IMF
  
- **BOX_MPC_OVER_h and SOURCE_REDSHIFT**: Must exactly match LC module settings, otherwise planes won't be found

---

## Input File Formats

### filters.dat

Simple list of filter names (one per line). Each filter name corresponds to a subdirectory under `../files/filters/` containing the filter response curve.

```
Roman_WFI_f158
Roman_WFI_f129
Roman_WFI_f106
Roman_WFI_f146
```

**Note:** Each filter subdirectory must contain the response curve file (e.g., `Roman_WFI_f158.dat`)

### Filter Response Files

Located in `../files/filters/<filter_name>/`, containing wavelength and response data.

**Format:**
```
Wavelength(AA)  Response
2500.0          0.0
2510.0          0.001
2520.0          0.003
...
```

### planes_list.txt (from LC module)

Same format as produced by LC module:
```
Plane#  Redshift  NearDist(cMpc/h)  FarDist(cMpc/h)  BoxReplica  SnapshotID  SnapshotZ
1       0.0109    29.91             35.00            0           98          0.01
...
51      0.6813    1706.37           1715.00          50          60          0.68
```

### coords.lc.*.txt (from LC module)

Particle coordinate catalog from LC module:
```
ID  X(Mpc/h)  Y(Mpc/h)  Redshift  Mass(Msun)  InitialMass(Msun)  Metallicity  -  Age(Gyr)  -  CMz_Subhalo  Npart_Subhalo
```

---

## Building the Module

```bash
cd /Users/pmsanch1/code/FORECAST/df
make clean
make
```

This produces the executable `executable_df`.

---

## Running the Module

### Prerequisites for Running

Ensure you have:
1. Completed all planes with the LC module
2. Generated all `coords.lc.*.txt` files
3. Generated `planes_list.txt` from LC module
4. Updated `df.ini` with correct paths and model settings

### Single Plane Execution

```bash
cd /Users/pmsanch1/code/FORECAST/df
./executable_df <snapshot_id> <restart_file_prefix>
```

**Arguments:**
- `<snapshot_id>`: TNG snapshot number to process (integer, e.g., 60)
  - Must be a snapshot used in planes_list.txt
  - If multiple planes use the same snapshot, they will be processed together

- `<restart_file_prefix>`: Base name for restart/plane tracking file
  - Appends `.d` suffix to create `<prefix>.d`
  - File contains the plane number (1-indexed) to process
  - Example: `plane_num` → reads from `plane_num.d`

**Example:**
```bash
./executable_df 60 plane_num
```

This reads plane number from `plane_num.d`, and processes snapshot 60 for that plane. Creates output file `flux.df.0060_51.txt` (if processing plane 51).

### Important Implementation Detail

The DF module **MUST BE RUN FOR EACH PLANE**, just like LC. The workflow is:

1. Update restart file with plane number (1-indexed)
2. Determine which snapshot that plane uses from `planes_list.txt`
3. Run: `./executable_df <snapshot_id> <restart_file_prefix>`
4. Update restart file to next plane number
5. Repeat for all planes

**Example batch workflow:**
```bash
for plane in {1..51}; do
  snapshot=$(grep "^$plane " ../lc/planes_list.txt | awk '{print $6}')
  echo $plane > plane_num.d
  ./executable_df $snapshot plane_num
done
```

### Processing Multiple Planes per Snapshot

If multiple planes use the same snapshot (common due to lightcone tiling), the DF module processes them in sequence. Each call should specify the same snapshot ID, and the restart file determines which plane to process within that snapshot.

---

## Output Files

### Flux Catalog: flux.df.<snapshot>_<plane>.txt

**Format** (space-separated columns):
```
ID  X(Mpc/h)  Y(Mpc/h)  Redshift  Mass(Msun)  InitialMass(Msun)  Metallicity  CMz_Subhalo  Age(Gyr)  Npart_Subhalo  F_filter1  F_filter2  ... F_filterN
```

**Column Details:**

| Column | Type | Description |
|--------|------|-------------|
| ID | int | Particle ID (from snapshot) |
| X, Y | float | Transverse coordinates in Mpc/h |
| Redshift | float | Particle redshift (same as LC output) |
| Mass | float | Current stellar mass in M☉ (total mass in particles) |
| InitialMass | float | Initial stellar mass in M☉ (at formation) |
| Metallicity | float | Metallicity (mass fraction) |
| CMz_Subhalo | float | Center-of-mass z-coord of parent subhalo |
| Age | float | Stellar age in Gyr (computed from formation redshift) |
| Npart_Subhalo | int | Number of particles in parent subhalo |
| F_filter1...N | double | Dust-free flux (uJy) in each filter, in order from filters.dat |

**Example output:**
```
0    100.5    -50.2    0.68    1.2e10    1.5e10    0.02    1205.4    2.3    45    0.234    0.156    0.089    0.045
1    102.1    -48.9    0.681   9.8e9     1.3e10    0.018   1206.1    2.5    45    0.198    0.134    0.075    0.038
...
```

**Units:**
- Fluxes: **microjansky (µJy or uJy)**
- Magnitude conversion: If needed, compute `m_AB = 23.9 - 2.5*log10(f_uJy)`

### Summary Statistics (Console Output)

The DF module prints:

```
... Reading planes_list.txt file ...
( 1706.37, 1715.00 ), 0060, 0.68
... Reading filter list ...
Nfilter =  4
... Reading SPS tables ...
(BC03 or CB16 tables loaded...)
N4_tot = 51234 stellar particles
... computing Dust-free SED fluxes per particle...
****-fluxes computed-****
... Writing the particle-based, dust-free flux catalogue ...
.. Flux file written ..
F_tot (total flux in fov [uJy]) for Roman_WFI_f158 filter: 1234.56
F_tot (total flux in fov [uJy]) for Roman_WFI_f129 filter: 987.65
...
M_tot (total mass in fov [M_sun]): 3.45e+11
N4_tot (total stellar particles in fov): 51234
execution time in [h] ...
```

---

## Computational Details

### SED Computation Process

For each stellar particle, the DF module:

1. **Loads stellar template**: Uses particle's age and metallicity to select/interpolate a stellar population synthesis model from BC03/CB16
   - Age interpolated to nearest available age bin
   - Metallicity interpolated to nearest available metallicity bin

2. **Computes SED**: Gets the wavelength-dependent luminosity $L_\lambda$ of the stellar particle

3. **Scales by mass**: Multiplies SED by initial stellar mass (accounting for stellar evolution)

4. **K-correction**: Applies redshift evolution to SED
   - Restframe wavelengths → observed wavelengths
   - Accounts for 1/(1+z) dimming of flux

5. **Filter integration**: Convolves SED with each filter response to compute apparent AB magnitude

6. **Flux conversion**: Converts magnitude to flux in microjansky:
   $$f_{uJy} = 10^{-0.4(m_{AB} - 23.9)}$$

### Stellar Population Models

#### BC03 Model Structure

**Reference:** Bruzual & Charlot 2003, updated 2012

**Spectral Properties:**
- Resolution: 1221 wavelength points
- Wavelength coverage: 3.5 - 160,000 Å (UV through far-IR)
- Good for broad SED studies, faster computation

**Directory Structure:**
```
bc03/
├── bc03_salpeter_imf/
│   ├── bc03_salpeter_imf_Z-1.0.sed     # Z/Z☉ = 0.0001
│   ├── bc03_salpeter_imf_Z-0.7.sed     # Z/Z☉ = 0.0004
│   ├── bc03_salpeter_imf_Z-0.4.sed     # Z/Z☉ = 0.004
│   ├── bc03_salpeter_imf_Z+0.0.sed     # Z/Z☉ = 0.02
│   ├── bc03_salpeter_imf_Z+0.3.sed     # Z/Z☉ = 0.05
│   ├── bc03_salpeter_imf_Z+0.7.sed     # Z/Z☉ = 0.2
│   ├── bc03_salpeter_imf_Z+1.0.sed     # Z/Z☉ = 0.5
│   └── ... (more metallicity files)
│
└── bc03_chabrier_imf/
    ├── bc03_chabrier_imf_Z-1.0.sed     # Same metallicity bins
    ├── bc03_chabrier_imf_Z-0.7.sed
    ├── ... (chabrier IMF variants)
```

**Metallicity Bins (6 discrete metallicities):**

| Code | Z/Z☉ | [Z/H] | Description |
|------|------|------|-------------|
| Z-1.0 | 0.0001 | -4.0 | Ultra-metal-poor (Population II) |
| Z-0.7 | 0.0004 | -3.4 | Metal-poor |
| Z-0.4 | 0.004  | -2.4 | Low metallicity |
| Z+0.0 | 0.02   | -1.4 | Solar neighborhood (subsolar) |
| Z+0.3 | 0.05   | -1.0 | Near-solar |
| Z+0.7 | 0.2    | -0.7 | Super-solar |
| Z+1.0 | 0.5    | -0.3 | Very super-solar |

**Age Bins (221 discrete ages):**
- Range: 1 Myr to 14 Gyr (Gyrillion years, age of universe)
- Spacing: Log-uniform with higher resolution at young ages
- Typical fine resolution at: 0-1 Gyr, coarser beyond 10 Gyr

**File Format (.sed files):**
Each metallicity file contains spectra at different ages (rows).
```
Wavelength(AA)  L_lambda_Age1(solar_lum)  L_lambda_Age2  L_lambda_Age3  ... L_lambda_Age221
3.5             1.23e+10                  5.67e+09      ...
7.0             2.45e+10                  8.90e+09      ...
...
160000          1.11e+05                  9.87e+04      ...
```

#### CB16 Model Structure

**Reference:** Conroy & van Dokkum 2012, updated 2016

**Spectral Properties:**
- Resolution: 13,391 wavelength points
- Wavelength coverage: 10 - 100,000 Å (optical/NIR dominant)
- Higher resolution for better accuracy in filter convolution
- Better for precise photometry

**Directory Structure:**
```
cb16/
├── cb16_salpeter_imf/
│   ├── cb16_salpeter_imf_Z0001.sed     # Z/Z☉ = 0.0001
│   ├── cb16_salpeter_imf_Z0005.sed     # Z/Z☉ = 0.0005
│   ├── cb16_salpeter_imf_Z001.sed      # Z/Z☉ = 0.001
│   ├── cb16_salpeter_imf_Z002.sed      # Z/Z☉ = 0.02
│   ├── cb16_salpeter_imf_Z005.sed      # Z/Z☉ = 0.05
│   ├── cb16_salpeter_imf_Z02.sed       # Z/Z☉ = 0.2
│   ├── cb16_salpeter_imf_Z05.sed       # Z/Z☉ = 0.5
│   └── cb16_salpeter_imf_Z1.sed        # Z/Z☉ = 1.0 (solar)
│
└── cb16_chabrier_imf/
    ├── cb16_chabrier_imf_Z0001.sed     # Same metallicity bins
    ├── cb16_chabrier_imf_Z0005.sed
    ├── ... (chabrier IMF variants)
```

**Metallicity Bins (8 discrete metallicities):**

| Code | Z/Z☉ | [Z/H] | Description |
|------|------|------|-------------|
| Z0001 | 0.0001 | -4.0 | Ultra-metal-poor |
| Z0005 | 0.0005 | -3.3 | Very metal-poor |
| Z001  | 0.001  | -3.0 | Metal-poor |
| Z002  | 0.02   | -1.4 | Solar neighborhood |
| Z005  | 0.05   | -1.3 | Below solar |
| Z02   | 0.2    | -0.7 | Super-solar |
| Z05   | 0.5    | -0.3 | Very super-solar |
| Z1    | 1.0    | 0.0  | Solar (Z☉ = 0.019) |

**Age Bins (245 discrete ages):**
- Range: 0.1 Myr to 14 Gyr
- Finer resolution than BC03, especially at young ages
- Better temporal resolution for star-forming galaxies

**File Format (.sed files):**
Similar to BC03, but with 13,391 wavelengths and 245 age steps.
```
Wavelength(AA)  L_lambda_Age1(solar_lum)  L_lambda_Age2  ... L_lambda_Age245
10              5.67e+09                  2.34e+09       ... 1.11e+08
15              7.89e+09                  3.45e+09       ... 1.56e+08
...
100000          9.87e+04                  8.76e+04       ... 1.23e+04
```

#### Initial Mass Function (IMF)

The IMF parameter determines how stellar masses are distributed in the population synthesis model. This affects the flux predictions, as different IMFs predict different numbers of stars at different masses.

**Salpeter IMF:**
$$\Phi(m) \propto m^{-2.35}$$

- Power-law exponent: -2.35
- Steep: More weight toward low-mass stars
- **Advantages:**
  - Classic, well-established IMF
  - Many observational calibrations available
  - Predicted to give more UV light from young populations
  
- **Disadvantages:**
  - Overproduces low-mass stars compared to modern surveys
  - Older model (1955)
  - Produces higher stellar masses for given light

**Chabrier IMF (Recommended):**
$$\Phi(m) = \begin{cases} \frac{dN}{dm} \propto \exp[-(log_{10}m - log_{10}m_c)^2/(2\sigma^2)] & m < 1 M_\odot \\ \propto m^{-2.3} & m \geq 1 M_\odot \end{cases}$$

- Lognormal for low masses, power-law for high masses
- Peak at ~0.1 M☉
- **Advantages:**
  - Modern, empirically calibrated (Chabrier 2003, 2005)
  - Better agreement with observed stellar mass function
  - Produces realistic low-mass star counts
  - Recommended for modern analyses
  
- **Disadvantages:**
  - More computationally complex
  - Fewer older legacy calibrations

**Impact on Flux Predictions:**

| Aspect | Salpeter | Chabrier |
|--------|----------|----------|
| Stellar Mass (same luminosity) | Higher | Lower |
| UV Flux (young, hot stars) | Higher | Lower |
| Integrated Light | Brighter overall | Dimmer overall |
| Mass-to-Light Ratio | Lower | Higher |
| Cool Dwarf Numbers | Lower | Higher |

**How IMF is Used in DF Module:**

1. **Model Loading:** Selects `bc03_salpeter_imf/` or `bc03_chabrier_imf/` directory based on `df.ini`
2. **Mass Scaling:** SPS model normalizes stellar mass to 1 M☉ per star
3. **Initial Mass:** Particle's `InitialMass` from LC output is multiplied by SED template
4. **Result:** Final flux accounts for both stellar evolution and initial mass distribution

### How to Set Up BC03/CB16 Files

1. **Download Models:**
   - BC03: http://www.bruzual.org/bc03/ (Bruzual & Charlot)
   - CB16: Via CDS Strasbourg or contact authors

2. **Extract and Organize:**
   ```bash
   mkdir -p bc03/bc03_salpeter_imf
   mkdir -p bc03/bc03_chabrier_imf
   # ... extract files ...
   ```

3. **Verify Structure:**
   ```bash
   ls bc03/bc03_salpeter_imf/bc03_salpeter_imf_Z*.sed  # Should show 6-8 files
   ```

4. **Update df.ini:**
   ```
   !...PATH_WHERE_BC03_IS
   /path/to/bc03
   !...MODEL_bc03_or_cb16
   cb16  # or bc03
   !...IMF_chabrier_or_salpeter
   chabrier  # or salpeter
   ```

### Model Comparison Summary

| Feature | BC03 | CB16 |
|---------|------|------|
| **Speed** | Faster (1221 wavelengths) | Slower (13,391 wavelengths) |
| **Accuracy** | Good | Better (higher resolution) |
| **Wavelength Coverage** | 3.5 - 160,000 Å | 10 - 100,000 Å |
| **Age Bins** | 221 | 245 |
| **Metallicity Bins** | 6-7 | 8 |
| **UV Accuracy** | Moderate | Limited (starts at 10 Å) |
| **Optical/NIR** | Good | Excellent |
| **Recommended For** | Quick analysis | Precise photometry |
| **Best With** | Salpeter | Chabrier |

---

**Recommendation:** Use **CB16 with Chabrier IMF** for most modern analyses. Use **BC03 with Salpeter IMF** if you need legacy consistency or faster computation for testing.

---

## Known Issues & Notes

### Metallicity Matching

The module uses nearest-neighbor matching for metallicity to available SPS bins. If a particle has metallicity outside the range of available models, it is clipped to the nearest available value.

### Age Interpolation

Stellar ages are interpolated to the nearest available age bin in the SPS models. This is necessary because models are discrete in stellar age.

### Memory Usage

Loading full SPS tables (especially CB16) can require significant memory (~2-4 GB). The module loads all tables at startup.

### Performance

- **BC03 mode**: Faster, ~10-60 seconds per plane
- **CB16 mode**: Slower due to higher resolution, ~30-120 seconds per plane

---

## Troubleshooting

### Error: "planes list file does not exists"

**Cause:** `planes_list.txt` not found in `../lc/`

**Solution:**
- Run LC module first to generate `planes_list.txt`
- Verify relative path is correct

### Error: "snapshot 60 not found in planes_list"

**Cause:** Specified snapshot ID doesn't match any planes for the given redshift

**Solution:**
- Check that `df.ini` BOX_MPC_OVER_h and SOURCE_REDSHIFT match LC module exactly
- Verify snapshot ID is correct
- Check `planes_list.txt` to see which snapshots are used

### Filter file not found

**Cause:** Filter directory missing or filter name incorrect

**Solution:**
- Verify filter names in `filters.dat` match subdirectories under `../files/filters/`
- Ensure filter response files exist: `../files/filters/<filter_name>/<filter_name>.dat`

### Very small fluxes or all zeros

**Cause:** 
- Age or metallicity outside model range
- Particle has very low stellar mass
- Filter is far from stellar emission peak

**Solution:**
- Check particle properties (age, metallicity) are reasonable
- Verify SPS model covers relevant metallicity range
- Check filter wavelength coverage

---

## Performance Considerations

### Typical Execution Times

- Single plane with BC03: 10-60 seconds
- Single plane with CB16: 30-120 seconds
- Full lightcone (50 planes): 15-120 minutes total

### Memory Requirements

- BC03 tables: ~200 MB
- CB16 tables: ~1-2 GB
- Particle catalog buffer: ~10-100 MB per plane
- Total use per plane: 500 MB - 2.5 GB

---

## Citation

If you use this module, please cite:

Fortuni, F., et al. (2023). FORECAST: A Fast Lightcone Simulation. *arXiv:2305.19166*

---

## Contact & Support

For issues, questions, or modifications:
- Original author: Ciro Giocoli (cgiocoli@gmail.com)
- Current maintainer: Flaminia Fortuni (flaminia.fortuni@inaf.it)
- Repository: https://github.com/flaminiafortuni/FORECAST
