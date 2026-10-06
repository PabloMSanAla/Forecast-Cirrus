# Spatially-Resolved Dust Attenuation Modeling

The **DC (Dust Correction)** module models interstellar and circumgalactic dust absorption by coupling a two-phase stellar birth-cloud prescription with the physical gas distribution in the simulation (Fortuni et al. 2023, Nelson et al. 2019).

---

## 1. Two-Component Attenuation Model

Following Charlot & Fall (2000), dust attenuation depends on stellar age $t_*$:

1. **Young Stars ($t_* \le 10\text{ Myr}$)**: Reside within their dense parent molecular birth clouds and experience both birth-cloud dust and diffuse ISM dust:
   $$\tau_{\text{young}}(\lambda) = \tau_{\text{BC}}(\lambda) + \tau_{\text{ISM}}(\lambda) \propto \exp\left( -1.0 \times \left(\frac{\lambda}{5500\text{ \AA}}\right)^{-0.7} \right)$$
2. **Older Stars ($t_* > 10\text{ Myr}$)**: Have disrupted their birth clouds and experience only the diffuse ambient ISM dust:
   $$\tau_{\text{old}}(\lambda) = \tau_{\text{ISM}}(\lambda) \propto \exp\left( -0.3 \times \left(\frac{\lambda}{5500\text{ \AA}}\right)^{-0.7} \right)$$

---

## 2. Gas-Traced Column Density Integration

Rather than adopting a simple empirical scaling (e.g. SFR or stellar mass), FORECAST uses the **Voronoi gas cells (PartType0)** from the cosmological simulation to measure the actual neutral hydrogen column density $N_{\text{HI}}$ and gas-phase metallicity $Z_{\text{gas}}$ in front of each star particle.

For each gas cell $j$ in front of a subhalo's stellar center of mass:
1. **Neutral Hydrogen Mass**: Derived from gas density $\rho_j$, internal energy $u_j$, and electron abundance $x_{e,j}$ via collisional and photoionization equilibrium fits (Nelson et al. 2019):
   $$n_{\text{HI}, j} = \mathcal{F}(T_j, \rho_j) \times \rho_j$$
2. **Column Density & Metallicity**:
   $$N_{\text{HI}} = \sum_{j \in \text{LOS}} n_{\text{HI}, j} \cdot L_j \quad [\text{cm}^{-2}], \quad \langle Z_{\text{gas}} \rangle = \frac{\sum_j Z_j M_{\text{HI}, j}}{\sum_j M_{\text{HI}, j}} \quad [Z_\odot]$$

---

## 3. Extinction Curve & Attenuated Photometry

The diffuse optical depth is computed using the Cardelli, Clayton & Mathis (1989, CCM89) Milky Way extinction curve with $R_V = 3.1$:

$$A(\lambda) = \left( a(x) + \frac{b(x)}{R_V} \right) A(V), \quad x = \frac{1}{\lambda}\; [\mu\text{m}^{-1}]$$

$$\tau_{\text{dust}}(\lambda) = \text{ModelC}(N_{\text{HI}}, \langle Z_{\text{gas}} \rangle) \times \frac{A(\lambda)}{A(V)}$$

The dust-attenuated composite galaxy spectrum is integrated over the telescope filters to produce reddened apparent fluxes $f_{\text{dc}, i}$ and correction ratios $d_{f, i} = f_{\text{dc}, i} / f_{\text{df}, i} \le 1.0$.
