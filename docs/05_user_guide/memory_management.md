# Memory Management & RAM Ceilings

FORECAST is engineered to operate strictly within user-defined memory ceilings (e.g. 2 GB, 4 GB, 8 GB, 16 GB), preventing Out-Of-Memory (OOM) crashes on large cosmological simulation datasets.

---

## 1. Streaming Architectures

### `lc` and `df` Modules
- **Direct Contiguous Ingestion**: Eliminates intermediate 3D coordinate matrices.
- **Bounded Buffer Spooling**: Batches particle selections in blocks of $B = 100,000$ particles.
- **Peak RSS**: Bounded to $< 450\text{ MB}$ in `lc` and $< 35\text{ MB}$ in `df`.

---

## 2. Dynamic Subhalo Chunking in `dc`

In the `dc` module, computing dust attenuation for tens of thousands of galaxies requires evaluating 6,900-bin spectra.

- **Dynamic Chunk Sizing**: Automatically estimates the available RAM budget:
  $$\text{Chunk Size} = \min\left(N_{\text{subhalos}}, \left\lfloor \frac{(\text{Memory Limit} - \text{Base RAM}) \times 0.70}{6900 \times 16\text{ bytes}} \right\rfloor\right)$$
- **High RAM Systems (8–16 GB)**: Processes all galaxies in a single pass for maximum speed.
- **Constrained Systems (2–4 GB)**: Processes galaxies in chunks, releasing spectral memory immediately after each batch to guarantee peak RSS stays below the ceiling.

---

## 3. Darwin & Linux Real-Time Accounting

All modules monitor process memory in real time via `getrusage(RUSAGE_SELF, ...)`:
- If peak RSS exceeds the ceiling, the process terminates safely with **Exit Code 3**.
