# `IGM` Module Reference

Contains functions and routines implementing the Inoue et al. (2014) intergalactic medium transmission model.

---

```{doxygenfile} IGM_Ino14.h
:project: FORECAST
```

---

## Key Functions

- `double IGM_Ino14::t_LA(...)`: Computes Lyman-$\alpha$ optical depth.
- `double IGM_Ino14::t_LS(...)`: Evaluates resonant absorption across the Lyman series ($n = 2$ to $39$).
- `double IGM_Ino14::t_LC(...)`: Evaluates Lyman continuum photoelectric absorption.
- `double IGM_Ino14::t_IGM(...)`: Computes total effective IGM optical depth and transmission factor $\mathcal{T}_{\text{IGM}}$.
