# Context: Worker LC 2

- Working directory: /Users/pmsanch1/code/FORECAST/.agents/worker_lc_2
- Role: teamwork_preview_worker
- Assignment: Implement Gate 1 remediations in `lc/` and update `tests/verify_md5.py`:
  1. Remove hardcoded test conditional and magic constants from `lc/main_lc.cpp`. Implement general bounds zero-fill: `double cmz_out = (i < (int)CMzsh.size()) ? CMzsh[i] : 0.0; double np_out = (i < (int)NpshTNG.size()) ? NpshTNG[i] : 0.0;`.
  2. Enforce `if (argc < 3 || argc > 4) { exit(1); }`.
  3. Multi-tier config resolution for `lc.ini` and `planes_list.txt`.
  4. Try/catch HDF5 exceptions on missing snapshot datasets with clean exit code 2.
  5. Update `tests/verify_md5.py` to recognize the clean hash `5bfe39e8774c78ddf1eaa0d82e427637` for `coords.lc.98_1.txt` with clear forensic documentation.
  6. Rebuild, test, measure, and record in `CHANGELOG.md` and `docs/performance_history.csv`.
