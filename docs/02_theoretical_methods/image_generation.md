# Image Generation & Mock Observation Synthesis

The post-processing suite turns particle-level flux catalogs into scientific FITS images and observationally realistic mock galaxy surveys.

---

## 1. Pixel Grid Rasterization (`create_image`)

For each lightcone slice (plane) and each photometric filter:
1. A 2D regular pixel matrix is allocated with user-specified dimensions $N_{\text{pix}} \times N_{\text{pix}}$ and pixel scale $s_{\text{pix}}$ (e.g. $0.06''/\text{pixel}$ for Roman WFI or $0.03''/\text{pixel}$ for JWST NIRCam).
2. Projected particle coordinates $(\theta_x, \theta_y)$ are mapped to discrete pixel indices $(p_x, p_y)$:
   $$p_x = \left\lfloor \frac{\theta_x + \theta_{\text{FoV}}/2}{s_{\text{pix}}} \right\rfloor, \quad p_y = \left\lfloor \frac{\theta_y + \theta_{\text{FoV}}/2}{s_{\text{pix}}} \right\rfloor$$
3. Fluxes $f_{\text{igm}, i}$ are accumulated into the pixel grid.
4. Output is written as a standard 16-bit or 32-bit floating-point **FITS** file with complete **WCS** (World Coordinate System) header keywords.

---

## 2. Multi-Plane Stacking (`sum_images.py`)

Individual plane images are stacked along the lightcone axis to create the composite deep-field image covering the entire redshift range:

$$I_{\text{total}}(x, y) = \sum_{i=0}^{N-1} I_{\text{plane}, i}(x, y)$$

---

## 3. Mock Observational Effects (PSF & Sky Noise)

To mimic real telescope imaging:
- **Point Spread Function (PSF)**: Convolved with realistic wavelength-dependent optical PSFs (e.g., WebbPSF for JWST or GalSim Roman models):
  $$I_{\text{conv}} = I_{\text{total}} \otimes \text{PSF}(\lambda)$$
- **Sky Background & Detector Noise**: Poisson background photon noise and Gaussian readout noise are added:
  $$I_{\text{obs}}(x, y) = I_{\text{conv}}(x, y) + \mathcal{P}(\mu_{\text{sky}}) + \mathcal{N}(0, \sigma_{\text{read}}^2)$$
