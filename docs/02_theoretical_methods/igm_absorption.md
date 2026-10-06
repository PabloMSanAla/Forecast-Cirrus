# Intergalactic Medium (IGM) Attenuation

The **IGM** module models resonant scattering and photoelectric absorption by neutral hydrogen clouds in the intergalactic medium along the line of sight between the emitter at redshift $z_{\text{em}}$ and the observer at $z = 0$.

---

## 1. Inoue et al. (2014) Analytic Model

FORECAST implements the state-of-the-art prescription from **Inoue, Shimizu, Iwata & Zheng (2014, MNRAS 442, 1805)**.

The mean IGM transmission function $\langle \mathcal{T}_{\text{IGM}}(\lambda_{\text{obs}}, z_{\text{em}}) \rangle$ is decomposed into two components:

$$\langle \mathcal{T}_{\text{IGM}}(\lambda_{\text{obs}}, z_{\text{em}}) \rangle = \exp\left( -\tau_{\text{Ly,series}}(\lambda_{\text{obs}}, z_{\text{em}}) - \tau_{\text{Ly,cont}}(\lambda_{\text{obs}}, z_{\text{em}}) \right)$$

### 1.1 Resonant Lyman Series Scattering
Accounts for resonant absorption transitions from the ground state $n=1$ to $n \ge 2$ (Ly$\alpha$, Ly$\beta$, Ly$\gamma$, up to the Lyman limit $\lambda_{\text{LL}} = 911.75\text{ \AA}$):

$$\tau_{\text{Ly,series}}(\lambda_{\text{obs}}, z_{\text{em}}) = \sum_{j=2}^{39} \tau_{1, j}(\lambda_{\text{obs}}, z_{\text{em}})$$

where each transition $j$ absorbs at rest wavelength $\lambda_j = 911.75 \times \frac{j^2}{j^2 - 1}\text{ \AA}$.

### 1.2 Lyman Continuum Photoelectric Absorption
Photons emitted below the rest-frame Lyman limit ($\lambda_{\text{rest}} \le 911.75\text{ \AA}$) ionize neutral hydrogen in intervening Lyman-limit systems (LLS) and Damped Ly$\alpha$ systems (DLAs):

$$\tau_{\text{Ly,cont}}(\lambda_{\text{obs}}, z_{\text{em}}) = \int_0^{z_{\text{em}}} dz' \int_0^\infty dN_{\text{HI}} \frac{\partial^2 N}{\partial z' \partial N_{\text{HI}}} \left( 1 - e^{-\tau_{\text{c}}(\lambda_{\text{obs}}, z', N_{\text{HI}})} \right)$$

---

## 2. Fast Filter Invariant Precomputation

For performance optimization, the IGM transmission is precomputed for all filter bandpasses across redshift bins, enabling fast $O(1)$ evaluation for millions of star particles without redundant numerical quadrature.
