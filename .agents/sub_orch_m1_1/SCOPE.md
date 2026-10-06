# Scope: Milestone 1 — LC Module Optimization & RAM Ceiling

## Mission
Refactor, optimize, and verify the LC module (`lc`) in `/Users/pmsanch1/code/FORECAST/lc` to enforce dynamic RAM awareness (4GB, 8GB, 16GB limits), achieve $\ge 20\%$ single-core speedup without internal threading/OpenMP, validate CLI plane arguments against `planes_list.txt`, and guarantee 100% bit-exact MD5 match against baseline for test planes (Rows 1, 2, 4).

## Assigned Features
- **F1: LC CLI Interface & Plane Validation**:
  - Accept `./executable_lc <snapshot> <plane_number> [memory_ceiling_gb]`.
  - Eliminate `.d` file requirement.
  - Read and validate plane number and snapshot against `planes_list.txt` before execution.
  - Exit with non-zero code if validation fails.
  - Align output naming with 0-indexed baseline format: `coords.lc.<snapshot>_<plane_number>.txt` (`coords.lc.98_0.txt`, `coords.lc.98_1.txt`, `coords.lc.98_3.txt`).
- **F2: LC Dynamic RAM Ceiling & Streaming Ingestion**:
  - Accept memory ceiling (4GB, 8GB, 16GB) via CLI or default.
  - Implement streaming HDF5 file processor: filter particles chunk-by-chunk directly into field-of-view, discarding non-matching particles immediately instead of holding all 20M particles in memory.
  - Keep peak RSS $\le 250$MB, completely eliminating OOM risks.
  - Monitor RSS via Darwin-aware `getrusage()`.
- **F3: LC Deterministic Single-Core Optimization**:
  - Pass `getY` arguments by `const&` (eliminates ~80M heap vector copies).
  - Hoist invariant `t0 = getY(z_tlist, age_tlist, zsim)` evaluation out of the particle loop.
  - Remove dead $O(K \times N)$ loop populating unused `NpTNG`.
  - Replace `pow(..., 2)` with simple multiplication (`dx * dx`).
  - Optimize COM loop to single pass.
  - Buffer file I/O and replace `std::endl` flushes with `\n`.
  - Achieve $\ge 20\%$ (target 40-60%) speedup without internal multi-threading/OpenMP.
- **F4: LC Bit-Exact Output Verification**:
  - Target MD5s for `/Volumes/PMSAdrive/pmsa/storage/TNG/output_optimized/lc/`:
    - `coords.lc.98_0.txt`: `79ac9efb68c8ce6e08b1c7c09dd887ab`
    - `coords.lc.98_1.txt`: `b1fc04316bb7a955d4f5df47a90628f7`
    - `coords.lc.98_3.txt`: `9f9ff464b433c58f4104881a0efaa748`
  - Strict preservation of arithmetic precision, RNG logic, and particle sequence.

## Code Layout Ownership
- Exclusively owns `lc/` directory (`main_lc.cpp`, `readTNGParticle.cpp`, `readTNGParticle.h`, `functions.cpp`, `functions.h`, `Makefile`).
- Must NOT modify `df/` or `tests/`.

## Reference Documents
- `ORIGINAL_REQUEST.md`: `/Users/pmsanch1/code/FORECAST/.agents/ORIGINAL_REQUEST.md`
- `PROJECT.md`: `/Users/pmsanch1/code/FORECAST/.agents/teamwork_preview_orchestrator_1/PROJECT.md`
- Explorer 1 Survey Report: `/Users/pmsanch1/code/FORECAST/.agents/explorer_survey_1/report.md`
- Explorer 3 Survey Report: `/Users/pmsanch1/code/FORECAST/.agents/explorer_survey_3/report.md`
