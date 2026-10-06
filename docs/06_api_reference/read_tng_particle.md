# `readTNGParticle` Class Reference

The `readTNGParticle` class handles low-level HDF5 file ingestion from IllustrisTNG simulation snapshots, FOF subhalo tables, and offset files.

---

```{doxygenclass} readTNGParticle
:project: FORECAST
:members:
:protected-members:
:undoc-members:
```

---

## Key Methods

- `void Initialize(std::string workdir, int particleID)`: Sets template file paths for snapshot directories, groups, and offsets.
- `void readHeader(int chunkID)`: Ingests snapshot header metadata (box size, redshift, cosmological parameters, particle counts).
- `void readStars(int chunkID)`: Ingests star particle coordinates, masses, metallicity, and formation time from `PartType4`.
- `void readGAS(int chunkID)`: Ingests gas cell coordinates, masses, densities, metallicities, and electron abundances from `PartType0`.
- `void readFof(int chunkID)`: Reads SubFind halo and subhalo length tables (`SubhaloLenType`).
- `void readOffset()`: Ingests offset indices (`SnapByType`) to map global particle IDs to subhalo structures.
