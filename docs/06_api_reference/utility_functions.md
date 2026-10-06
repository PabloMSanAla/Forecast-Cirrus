# Utility Functions Reference (`functions.h`)

Core utility routines for string formatting, cosmological calculations, and I/O buffer management.

---

```{doxygenfile} functions.h
:project: FORECAST
```

---

## Key Functions

- `void readParameters(...)`: Parses module `.ini` files and resolves environment variable overrides.
- `double getY(vector<double> x, vector<double> y, double xi)`: Performs robust 1D spline / linear interpolation.
- `double getPeakRSS_MB()`: Measures real-time process peak resident set size (RSS) in MB across Darwin (macOS) and Linux.
- `void checkMemoryCeiling(double ceiling_gb)`: Validates memory against the user limit and exits with code 3 upon breach.
