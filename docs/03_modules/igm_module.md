# Module 4: IGM Attenuation (IGM)

The **IGM** module computes resonant Lyman series scattering and photoelectric Lyman continuum absorption caused by neutral hydrogen clouds in the intergalactic medium between the source and the observer.

---

## Purpose & Overview
- Ingests dust-corrected particle catalogs (`flux.dc.<snap>_<plane>.txt`).
- Evaluates the Inoue et al. (2014) mean IGM transmission function $\langle \mathcal{T}_{\text{IGM}}(\lambda_{\text{obs}}, z) \rangle$.
- Integrates the attenuated spectra across telescope filters to generate the final observed fluxes $f_{\text{igm}, i}$ in $\mu\text{Jy}$.
- Produces the final simulation catalog `flux.igm.<snap>_<plane>.txt`, ready for image synthesis and mock catalog generation.

---

## Key Files & Implementation
- **Executable**: `igm/executable_igm`
- **Main Driver**: `igm/main_igm.cpp`
- **IGM Model**: `igm/IGM_Ino14.h`, `igm/IGM_Ino14.cpp`
- **Spectral Engine**: `igm/SED.h`, `igm/SED.cpp`
- **Configuration**: `igm/igm.ini`
- **Parallel Runner**: `igm/igm.sh`
