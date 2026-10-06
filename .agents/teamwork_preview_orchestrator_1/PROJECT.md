# Project: FORECAST Pipeline LC & DF Optimization

## Architecture
- **Pipeline Flow**:
  1. Simulation Snapshots (HDF5 particles in `/Volumes/PMSAdrive/pmsa/storage/TNG/TNG50-2/`) $\to$ **LC Module** (`./executable_lc <snapshot> <plane_number> [mem_gb]`) $\to$ Projected lightcone coordinate catalog (`coords.lc.<snap>_<plane>.txt` in `output_optimized/lc/`).
  2. Lightcone Coordinates Catalog $\to$ **DF Module** (`./executable_df <snapshot> <plane_number> [mem_gb]`) $\to$ Dust-free stellar photometry catalog (`flux.df.<snap>_<plane>.txt` in `output_optimized/df/`).
- **External Parallelization**:
  Pipelines run externally per snapshot and per plane. Strictly **NO** internal threading or OpenMP inside `lc` and `df`.
- **Memory Management Architecture**:
  - `lc`: Streaming HDF5 chunk processor. Inspects and filters particles chunk-by-chunk directly into FoV, discarding non-matching particles immediately. RSS bounded to ~150-250MB.
  - `df`: Streaming particle batch processor. Ingests particles in fixed batches ($B = 100,000$), computes photometry, and streams output directly to disk. RSS bounded to $\le 80$MB.
  - Dynamic monitoring: Both modules monitor/enforce memory limits (4GB, 8GB, 16GB) using Darwin-aware RSS checks (`ru_maxrss` in bytes).

## Feature Inventory
| # | Feature | Description | Milestone | Source |
|---|---------|-------------|-----------|--------|
| F1 | LC CLI Interface & Plane Validation | Parse `<snapshot> <plane_number>` directly from CLI; eliminate `.d` file dependency; validate plane/snapshot pair against `planes_list.txt` before execution; fail-fast with non-zero exit code on invalid arguments. | M1 | Survey E1, E3 |
| F2 | LC Dynamic RAM Ceiling & Streaming Processing | Accept user-specified memory ceiling (4GB, 8GB, 16GB); stream HDF5 chunks; keep peak RSS $\le 250$MB; eliminate all OOM risks. | M1 | Survey E1 |
| F3 | LC Deterministic Single-Core Optimization | Pass `getY` by `const&`; hoist invariant `t0`; remove dead `NpTNG` loop; replace `pow(..., 2)` with multiply; optimize COM calculation; buffer file I/O; achieve $\ge 20\%$ speedup. | M1 | Survey E1 |
| F4 | LC Bit-Exact Output Verification | Ensure 100% MD5 checksum match against baseline for test planes (`98_0`, `98_1`, `98_3`). | M1 | Survey E1, E3 |
| F5 | DF CLI Interface & Plane Validation | Parse `<snapshot> <plane_number>` directly from CLI; multi-tier path resolution for `planes_list.txt`; validate plane/snapshot pair; fail-fast with non-zero exit code on invalid arguments. | M2 | Survey E2, E3 |
| F6 | DF Dynamic RAM Ceiling & Streaming Processing | Accept user-specified memory ceiling (4GB, 8GB, 16GB); batch particle photometry ($B = 100,000$); keep peak RSS $\le 80$MB; eliminate all OOM risks. | M2 | Survey E2 |
| F7 | DF Deterministic Single-Core Optimization | Remove inner-loop debug `cout` printing; precalculate/cache filter curves and denominator integrals; zero-copy `SEDbc03_interp_2spec`; in-place `z_evol`; buffer file I/O; achieve $\ge 20\%$ (40-65%) speedup. | M2 | Survey E2 |
| F8 | DF Bit-Exact Output Verification | Ensure 100% MD5 checksum match against baseline for test planes (`98_0`, `98_1`, `98_3`). | M2 | Survey E2, E3 |
| F9 | E2E Test Suite & Verification Harnesses | Implement opaque-box test runner for Tiers 1-4 (MD5 verification, Darwin RSS monitoring, wall-clock speedup verification, CLI plane validation); publish `TEST_READY.md`. | E2E | Survey E3 |
| F10 | Complete Audit Trail & Performance History | Maintain `CHANGELOG.md` per change_tracker skill; update `docs/performance_history.csv`; generate comprehensive `validation_report.md`. | M3 | Survey E3, SKILL.md |

## Milestones
| # | Name | Scope | Dependencies | Status |
|---|------|-------|-------------|--------|
| E2E | E2E Testing Track | Test infra, verification harnesses (MD5, RAM, Speedup, CLI), Tiers 1-4 tests, `TEST_READY.md` | none | DONE |
| M1 | LC Module Optimization & RAM Ceiling | Features F1, F2, F3, F4 | none | DONE |
| M2 | DF Module Optimization & RAM Ceiling | Features F5, F6, F7, F8 | none | DONE |
| M3 | E2E Pass, Adversarial Hardening & Audit | Features F9, F10; Tiers 1-4 E2E test pass; Tier 5 adversarial hardening; `CHANGELOG.md`, `performance_history.csv`, `validation_report.md` | E2E, M1, M2 | DONE |

## Interface Contracts
### CLI Interface (both `lc` and `df`)
- Usage: `./executable_lc <snapshot> <plane_number> [memory_ceiling_gb]`
- Usage: `./executable_df <snapshot> <plane_number> [memory_ceiling_gb]`
- Exit codes:
  - `0`: Success
  - `1`: Invalid arguments or failed plane validation (plane not found in `planes_list.txt` or snapshot mismatch)
  - `2`: Missing configuration or input data files
  - `3`: Memory ceiling exceeded (safety limit breach)

### `lc` $\to$ `df` Data Contract
- File naming: `coords.lc.<snapshot>_<plane_number>.txt` (e.g. `coords.lc.98_0.txt`, `coords.lc.98_1.txt`, `coords.lc.98_3.txt`)
- Columns: 12 space-delimited numerical values matching baseline coordinates format.
- Bit-exact MD5 targets:
  - `coords.lc.98_0.txt`: `79ac9efb68c8ce6e08b1c7c09dd887ab`
  - `coords.lc.98_1.txt`: `b1fc04316bb7a955d4f5df47a90628f7`
  - `coords.lc.98_3.txt`: `9f9ff464b433c58f4104881a0efaa748`

### `df` Output Contract
- File naming: `flux.df.<snapshot>_<plane_number>.txt` (e.g. `flux.df.98_0.txt`, `flux.df.98_1.txt`, `flux.df.98_3.txt`)
- Columns: 14 space-delimited columns (default `std::ofstream` precision, trailing space before newline).
- Bit-exact MD5 targets:
  - `flux.df.98_0.txt`: `a9eb9b4aad5e6e65bc220b462005f2bd`
  - `flux.df.98_1.txt`: `cb8cdb62e2bf14bcbd6ff4c813044d80`
  - `flux.df.98_3.txt`: `acbbb175ac0052dec2808c583b4a0d7d`

## Code Layout
- `lc/`: LC module source code (`main_lc.cpp`, `readTNGParticle.cpp`, `readTNGParticle.h`, `functions.cpp`, `functions.h`, `Makefile`).
- `df/`: DF module source code (`main_df.cpp`, `SED.cpp`, `SED.h`, `functions.cpp`, `functions.h`, `Makefile`).
- `tests/`: Automated test harnesses and verification scripts (`verify_md5.py`, `monitor_rss.py`, `benchmark_speedup.py`, `test_cli.py`, `run_e2e_tests.sh`).
- `CHANGELOG.md`: Human-readable audit log tracking all actions, rationales, performance deltas, and RAM deltas.
- `docs/performance_history.csv`: Machine-readable benchmark log.
- `validation_report.md`: Final acceptance report summarizing all criteria.
