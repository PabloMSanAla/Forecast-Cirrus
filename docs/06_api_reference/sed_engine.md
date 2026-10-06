# `SED` Class Reference

The `SED` class implements the Spectral Energy Distribution (SED) synthesis engine, bilinear SPS table interpolation, dust attenuation modeling, and synthetic filter bandpass integration.

---

```{doxygenclass} SED
:project: FORECAST
:members:
:protected-members:
:undoc-members:
```

---

## Key Methods

- `void extract_spec(...)`: Interpolates specific luminosity across age and metallicity grids.
- `void z_evol(...)`: Shifts rest-frame wavelength grid to observed cosmological frame and scales flux by luminosity distance $D_L(z)$.
- `void modelC(...)`: Computes Nelson et al. (2019) / Fortuni et al. (2023) Model C dust optical depth from $N_{\text{HI}}$ and $Z_{\text{gas}}$.
- `void dust_attenuation(...)`: Applies CCM89 extinction curve to the composite galaxy spectrum.
- `double compute_mab(...)`: Performs numerical integration of the attenuated spectrum against a filter transmission curve to calculate apparent AB magnitude.
