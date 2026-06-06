#%%
"""
Roman Space Telescope photometry for a stellar particle using PST
=================================================================
Given a stellar particle's age, current mass, initial mass, and metallicity,
this script:
  1. Loads a PopStar SSP model (Chabrier IMF) via PST.
  2. Interpolates the SED for the particle's age and metallicity.
  3. Scales the spectrum by the particle's initial mass.
  4. Computes synthetic photometry in four Roman WFI filters:
       F106, F129, F146, F158.
  5. Reports the flux in physical units and converts to micro-Janskys (μJy).

Requirements
------------
    pip install population-synthesis-toolkit astropy numpy

Roman filter transmission curves are fetched from the SVO Filter Profile
Service (https://svo2.cab.inta-csic.es/theory/fps/) the first time the
script is run; they are cached locally by PST afterwards.

Notes on SSP data
-----------------
PST's built-in PopStar SSP grids must be downloaded separately:
    https://population-synthesis-toolkit.readthedocs.io/en/latest/get_ssp_data.html

Alternatively, set `SSP_PATH` below to point to a local copy.
"""

import numpy as np
from astropy import units as u
import pandas as pd

# ── PST imports ──────────────────────────────────────────────────────────────
from pst.SSP import PopStar
from pst.observables import Filter, FilterList
from astropy.cosmology import Planck18
# ─────────────────────────────────────────────────────────────────────────────
# USER INPUTS — modify these values to describe your stellar particle
# ─────────────────────────────────────────────────────────────────────────────


filename = '/Volumes/T7/storage/TNG/forecast/lc/coords.lc.98_0.txt'

columns = ['id', 'x', 'y', 'z', 'mass', 'massinit', 'metallicity','notknown', 'age', 'notknown_2', 'cmz_subhalo', 'npart_subhalo']
df = pd.read_csv(filename, delimiter=' ', names=columns)

index = 0

# Define star particle parameters
p_age = df.loc[index, 'age']                # Age in Gyr
p_initial_mass = df.loc[index, 'massinit']  # M_sun
p_current_mass = df.loc[index, 'mass']      # M_sun (after stellar evolution)
p_metal = df.loc[index, 'metallicity']      # Solar metallicity


STELLAR_AGE      = p_age * 1e9 *u.yr                 # age of the stellar population  [yr]
MASS             = p_current_mass * u.Msun      # current (surviving) mass        [M_sun]
INITIAL_MASS     = p_initial_mass * u.Msun      # initial mass at formation       [M_sun]
METALLICITY      = p_metal                      # absolute metallicity Z (mass fraction)

# Redshift at which we observe the particle (0 = local)
Z_OBS            = 0                  # redshift of the particle (for k-correction)
SSP_PATH      = None             # None → PST default; or e.g. "/data/ssp"

# ─────────────────────────────────────────────────────────────────────────────
# Roman WFI filter identifiers on the SVO Filter Profile Service
# ─────────────────────────────────────────────────────────────────────────────
ROMAN_FILTERS = {
    "F106": "Roman_WFI.F106",
    "F129": "Roman_WFI.F129",
    "F146": "Roman_WFI.F146",
    "F158": "Roman_WFI.F158",
}

# ─────────────────────────────────────────────────────────────────────────────
# 1. Load SSP model
# ─────────────────────────────────────────────────────────────────────────────
print("Loading PopStar SSP model (Chabrier IMF)…")
kwargs = {} if SSP_PATH is None else {"path": SSP_PATH}
ssp = PopStar(IMF="cha", **kwargs)
print(f"  Ages       : {ssp.ages.min():.2e} – {ssp.ages.max():.2e}")
print(f"  Metallicity: {ssp.metallicities.min():.5f} – {ssp.metallicities.max():.5f}")
print(f"  Wavelength : {ssp.wavelength.min():.0f} – {ssp.wavelength.max():.0f}")

# ─────────────────────────────────────────────────────────────────────────────
# 2. Load Roman WFI filters
# ─────────────────────────────────────────────────────────────────────────────
print("\nLoading Roman WFI filters from SVO…")
filter_objects = []
filter_labels  = []
for label, svo_name in ROMAN_FILTERS.items():
    filt = Filter.from_svo(svo_name)
    filter_objects.append(filt)
    filter_labels.append(label)
    print(f"  {label:5s}  λ_eff = {filt.effective_wavelength():.0f}")

filter_list = FilterList(filter_objects)

# ─────────────────────────────────────────────────────────────────────────────
# 3. Pre-compute photometry on the full SSP grid  (PST-native)
#
#    ssp.compute_photometry() convolves every SSP SED with every filter and
#    stores the result in ssp.photometry, shape (n_filters, n_metallicities, n_ages).
#    Units: Lsun / Msun_initial  (specific luminosity per initial solar mass)
# ─────────────────────────────────────────────────────────────────────────────
print("\nPre-computing photometry on SSP grid (all filters × all ages × all Z)…")
phot_grid = ssp.compute_photometry(filter_list=filter_objects, z_obs=Z_OBS)
# phot_grid: astropy Quantity, shape (n_filters, n_Z, n_ages), units Lsun/Msun

print(f"  Photometry grid shape: {phot_grid.shape}  "
      f"units: {phot_grid.unit}")

# ─────────────────────────────────────────────────────────────────────────────
# 4. Interpolate the particle onto the SSP grid  (PST-native)
#
#    ssp.get_weights() performs bilinear interpolation in (age, metallicity)
#    space and returns a 2-D weight array  (n_Z, n_ages)  in units of Msun
#    when masses are supplied.  Here we pass initial_mass=1 Msun so the
#    weights sum to 1 — this gives us the *specific* flux.  We then multiply
#    by INITIAL_MASS at the end.
# ─────────────────────────────────────────────────────────────────────────────
print(f"\nInterpolating particle  (age={STELLAR_AGE:.2e}, Z={METALLICITY})…")

weights = ssp.get_weights(
    ages          = [STELLAR_AGE.to_value("yr")] * u.yr,
    metallicities = np.array([METALLICITY]),
    masses        = [1.0] * u.Msun,          # normalised to 1 Msun_initial
)
# weights shape: (n_Z, n_ages), units: Msun

# Contract:  sum over (Z, age)  →  scalar per filter
# phot_grid  shape: (n_filters, n_Z, n_ages)   [Lsun / Msun]
# weights    shape: (n_Z, n_ages)               [Msun]
# result     shape: (n_filters,)                [Lsun]  (specific: per 1 Msun_init)
specific_flux = (phot_grid * weights[np.newaxis, :, :]).sum(axis=(1, 2))
# specific_flux: Lsun / Msun * Msun = Lsun  (for 1 Msun_initial particle)

# Scale to the actual particle initial mass
total_flux = specific_flux * INITIAL_MASS          # Lsun  (total luminosity)

print(f"  Specific flux (per Msun_init): {specific_flux}")
print(f"  Total flux    (× {INITIAL_MASS:.1e}):    {total_flux}")

# ─────────────────────────────────────────────────────────────────────────────
# 5. Convert to F_ν  using FilterList.get_fnu()  (PST-native)
#
#    get_fnu() expects the SED as an astropy Quantity with spectral flux density
#    units.  We use it on the *per-filter* luminosities we already have.
#    The cleanest PST path for a fully-resolved SED is to reconstruct the
#    particle's SED from get_ssp_l_lambda and pass it to filter_list.get_fnu().
#
#    get_fnu(sed, distance) integrates  ∫ F_λ T dλ / ∫ T dλ  for each filter
#    and returns F_ν in Jy.
# ─────────────────────────────────────────────────────────────────────────────
print("\nConverting to F_ν via FilterList.get_fnu()…")

# Reconstruct the particle's full SED  [Lsun / Å]
l_lambda_specific = ssp.get_ssp_l_lambda(STELLAR_AGE, METALLICITY)   # Lsun/Å/Msun
l_lambda_total    = l_lambda_specific * INITIAL_MASS                   # Lsun/Å

# Distance: for absolute / distance-independent flux set d=10 pc (= D_mod 0).
# Change d_pc to your actual source distance to get apparent fluxes.
redshift = df.loc[index, 'z']  

d_pc = Planck18.luminosity_distance(redshift).to(u.pc)
# d_pc = 10.0 * u.pc   # ← change here, e.g. (10**((mu+5)/5)) * u.pc

# PopStar wavelength grid is not strictly monotonic — sort and deduplicate
sort_idx  = np.argsort(ssp.wavelength)
wl_sorted = ssp.wavelength[sort_idx]
monotonic_mask = np.concatenate([[True], np.diff(wl_sorted) > 0])
wl_clean       = wl_sorted[monotonic_mask]
filter_list.interpolate(wl_clean)

# Apply the same sort + monotonic mask to the SED
l_lambda_total = (l_lambda_specific * INITIAL_MASS)[sort_idx][monotonic_mask]
area = 4 * np.pi * d_pc.to(u.cm)**2          # cm²
f_lambda_total_area = l_lambda_total / area        # Lsun / Å / cm²
f_nu, _    = filter_list.get_fnu(f_lambda_total_area)
ab_mags, _ = filter_list.abmag(f_lambda_total_area)
# ─────────────────────────────────────────────────────────────────────────────
# 7. Print results
# ─────────────────────────────────────────────────────────────────────────────
f_nu_ujy = f_nu.to(u.uJy)   # micro-Janskys

print("\n" + "=" * 68)
print("  Roman WFI Photometry  (PST-native pipeline)")
print("=" * 68)
print(f"  Stellar age      : {STELLAR_AGE:.3e}")
print(f"  Current mass     : {MASS:.3e}")
print(f"  Initial mass     : {INITIAL_MASS:.3e}")
print(f"  Metallicity  Z   : {METALLICITY}")
print(f"  Redshift         : {Z_OBS}")
print(f"  Reference dist.  : {d_pc}")
print("-" * 68)
print(f"  {'Filter':<8}  {'F_ν (Jy)':>14}  {'F_ν (μJy)':>12}  {'AB mag':>8}")
print("-" * 68)
for i, label in enumerate(filter_labels):
    print(f"  {label:<8}  {f_nu[i].to_value('Jy'):>14.4e}  "
          f"{f_nu_ujy[i].value:>12.4f}  {ab_mags[i]:>8.3f}")
print("=" * 68)

# ─────────────────────────────────────────────────────────────────────────────
# Convenience function — loop over many particles efficiently
# ─────────────────────────────────────────────────────────────────────────────

def particle_roman_photometry(
    ssp_model,
    filter_list,
    stellar_age,
    initial_mass,
    metallicity,
    distance=10.0 * u.pc,
):
    """
    Compute Roman WFI photometry for a single stellar particle using PST.

    Parameters
    ----------
    ssp_model    : pst.SSP.SSPBase  — pre-loaded SSP (with photometry grid
                   already computed via ssp.compute_photometry(filter_list))
    filter_list  : pst.observables.FilterList
    stellar_age  : astropy Quantity [time] or float [yr]
    initial_mass : astropy Quantity [mass] or float [Msun]
    metallicity  : float — absolute metallicity Z (mass fraction)
    distance     : astropy Quantity [length], default 10 pc

    Returns
    -------
    dict with keys 'f_nu_jy', 'f_nu_ujy', 'ab_mag'  — each an array
    over filters in the same order as filter_list.
    """
    if not isinstance(stellar_age, u.Quantity):
        stellar_age = stellar_age * u.yr
    if not isinstance(initial_mass, u.Quantity):
        initial_mass = initial_mass * u.Msun

    # Full SED of the particle
    l_lam = ssp_model.get_ssp_l_lambda(stellar_age, metallicity) * initial_mass

    # PST-native photometry methods
    f_nu   = filter_list.get_fnu(l_lam, distance)        # Jy
    ab_mag = filter_list.abmag(l_lam, distance)

    return {
        "f_nu_jy"  : f_nu.to(u.Jy),
        "f_nu_ujy" : f_nu.to(u.uJy),
        "ab_mag"   : ab_mag,
    }
