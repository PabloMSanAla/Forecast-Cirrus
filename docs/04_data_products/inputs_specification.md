# Input Specifications & Data Formats

FORECAST ingests raw simulation snapshots and auxiliary cosmological/photometric lookup tables.

---

## 1. Cosmological Simulation Snapshots (IllustrisTNG Format)

FORECAST natively ingests HDF5 files formatted according to the [IllustrisTNG Data Specifications](https://www.tng-project.org/data/docs/specifications/).

### Stellar Particles (`PartType4`)
| Dataset Name | HDF5 Type | Description | Units in Simulation |
| :--- | :---: | :--- | :--- |
| `Coordinates` | `double[3]` | Comoving 3D spatial position | $\text{ckpc} / h$ |
| `Masses` | `double` | Current stellar particle mass | $10^{10} M_\odot / h$ |
| `GFM_InitialMass` | `double` | Initial stellar birth mass | $10^{10} M_\odot / h$ |
| `GFM_Metallicity` | `double` | Total metal mass fraction $Z_* = M_Z / M_{\text{tot}}$ | mass fraction |
| `GFM_StellarFormationTime` | `double` | Cosmic scale factor $a_*$ at particle birth | dimensionless |

### Gas Cells (`PartType0`)
| Dataset Name | HDF5 Type | Description | Units in Simulation |
| :--- | :---: | :--- | :--- |
| `Coordinates` | `double[3]` | Voronoi cell center position | $\text{ckpc} / h$ |
| `Masses` | `double` | Gas cell mass | $10^{10} M_\odot / h$ |
| `Density` | `double` | Comoving gas density | $(10^{10} M_\odot / h) / (\text{ckpc}/h)^3$ |
| `GFM_Metallicity` | `double` | Total gas metal mass fraction $Z_{\text{gas}}$ | mass fraction |
| `ElectronAbundance` | `double` | Fractional electron number density $x_e$ | dimensionless |
| `InternalEnergy` | `double` | Thermal energy per unit mass $u$ | $(\text{km}/\text{s})^2$ |

### Group Catalogs & Offsets
- **FOF Subhalo Tables (`fof_subhalo_tab_*.hdf5`)**: Contains `Subhalo/SubhaloLenType` ($6 \times N_{\text{sub}}$ matrix).
- **Offsets Files (`offsets_*.hdf5`)**: Contains `Subhalo/SnapByType` to map global particle indices to subhalos.

---

## 2. Auxiliary Files

- **`snaplist_TNG.txt`**: List of available simulation snapshot numbers sorted from $z = 0$.
- **`timelist_TNG.txt`**: Table of snapshot number, redshift $z$, and cosmic age (Gyr).
- **`LCDM-comovingdistTNG.dat`**: Comoving distance $D_c(z)$ and luminosity distance $D_L(z)$ lookups.
- **`filters.dat` & `filters/<filter>.dat`**: List of filter names and 2-column ASCII tables (wavelength in $\text{\AA}$, transmission $[0, 1]$).
- **`extinctionCCM89.dat`**: Cardelli, Clayton & Mathis (1989) Milky Way extinction curve.
