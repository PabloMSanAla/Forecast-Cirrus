# Troubleshooting & Exit Codes

FORECAST enforces standard POSIX exit codes across all executables to facilitate automated workflow orchestration.

---

## Standard Exit Codes

| Exit Code | Meaning | Cause & Recommended Action |
| :---: | :--- | :--- |
| **0** | **Success** | The plane computation completed successfully. |
| **1** | **CLI / Plane Validation Error** | Snapshot or plane number is invalid or not listed in `planes_list.txt`. Check your CLI arguments. |
| **2** | **Missing File / Input Error** | A required input file (`.ini`, `planes_list.txt`, `filters.dat`, BC03 tables, or HDF5 chunk) was not found. Check the file paths in your `.ini` file. |
| **3** | **Memory Limit Exceeded** | The process memory exceeded the configured memory ceiling (`-m`). Increase the limit (e.g. `-m 8.0`) or run fewer concurrent processes. |

---

## Frequently Encountered Issues

### 1. `HDF5 FOF catalog not found` (Exit 2)
Ensure that `snapdir_*` and `groups_*` directories match the snapshot number and that all HDF5 chunk files are readable.

### 2. `Filter file is missing` (Exit 2)
Verify that each filter listed in `files/filters.dat` has a corresponding transmission curve in `files/filters/<filter_name>.dat`.
