# Stellar Population Synthesis & Photometry

The **DF (Dust-Free)** module computes the intrinsic unattenuated spectral energy distribution (SED) and synthetic photometry for every star particle located inside the lightcone.

---

## 1. Single Stellar Population (SSP) Modeling

In cosmological hydrodynamical simulations, each star particle represents a coeval population of stars formed simultaneously from gas with initial mass $M_{*,\text{init}}$, age $t_*$, and metallicity $Z_*$.

The intrinsic rest-frame luminosity of a star particle is given by:

$$L_\lambda(\lambda_{\text{rest}}) = M_{*,\text{init}} \times \mathcal{S}_\lambda(t_*, Z_*)$$

where $\mathcal{S}_\lambda(t, Z)$ is the specific luminosity grid (in $L_\odot \text{ \AA}^{-1} M_\odot^{-1}$) derived from Stellar Population Synthesis (SPS) models:
- **BC03** (Bruzual & Charlot 2003): 6 metallicity values ($Z = 0.0001, 0.0004, 0.004, 0.008, 0.02, 0.05$) and 221 age steps across 6,900 wavelength bins ($91\text{ \AA} \le \lambda \le 160\text{ }\mu\text{m}$).
- **CB16** (Gutkin, Charlot & Bruzual 2016): 14 metallicity values ($Z = 0.0001$ to $0.040$).
- **Initial Mass Functions (IMF)**: Supports Chabrier (2003) and Salpeter (1955) IMFs.

---

## 2. 2D Bilinear Spectral Interpolation

For an arbitrary star particle with age $t_*$ and metallicity $Z_*$, FORECAST finds the closest metallicity grid tracks $Z_1 \le Z_* \le Z_2$ and closest age tracks $t_1 \le t_* \le t_2$, performing log-linear interpolation across all 6,900 spectral bins:

$$\mathcal{S}_\lambda(t_*, Z_*) = \text{interp}\left(\mathcal{S}_\lambda(t_1, Z_1), \mathcal{S}_\lambda(t_2, Z_1), \mathcal{S}_\lambda(t_1, Z_2), \mathcal{S}_\lambda(t_2, Z_2)\right)$$

---

## 3. Cosmological Flux & k-Correction

The observed monochromatic flux density at observed wavelength $\lambda_{\text{obs}} = (1 + z_{\text{los}}) \lambda_{\text{rest}}$ is:

$$f_\nu(\lambda_{\text{obs}}) = \frac{(1 + z_{\text{los}}) L_\lambda(\lambda_{\text{rest}})}{4 \pi D_L^2(z_{\text{los}})} \frac{\lambda_{\text{rest}}^2}{c}$$

where $D_L(z) = (1+z) D_c(z)$ is the cosmological luminosity distance.

---

## 4. Synthetic Filter Bandpass Integration

For a telescope filter bandpass with transmission curve $T_i(\lambda)$, the apparent AB magnitude $m_{\text{AB}, i}$ is calculated using the standard definition:

$$m_{\text{AB}, i} = -2.5 \log_{10} \left[ \frac{\int f_\nu(\lambda) T_i(\lambda) \frac{d\lambda}{\lambda}}{\int g_\nu(\lambda) T_i(\lambda) \frac{d\lambda}{\lambda}} \right] - 48.60$$

where $g_\nu = 3631\text{ Jy} = 3.631 \times 10^{-20}\text{ erg s}^{-1}\text{ cm}^{-2}\text{ Hz}^{-1}$ is the AB reference zero point.

The dust-free flux in microjanskys ($\mu\text{Jy}$) is:

$$f_{\text{df}, i} = 10^{\left(29.0 - \frac{m_{\text{AB}, i} + 48.60}{2.5}\right)} \quad [\mu\text{Jy}]$$
