# Parallel Batch Execution (`forecast.sh`)

The master shell script **`forecast.sh`** coordinates running all four FORECAST modules (`lc` $\to$ `df` $\to$ `dc` $\to$ `igm`) in parallel across multiple CPU cores using **GNU Parallel**.

---

## 1. Syntax & Options

```bash
./forecast.sh [options]
```

| Flag | Argument | Default | Description |
| :--- | :--- | :---: | :--- |
| `-n` | `<int>` | `1` | Number of parallel CPU workers |
| `-i` | `<int>` | `0` | Initial plane number to process |
| `-max` | `<int>` | `max` | Maximum plane number to process |
| `-lc` | `<path>` | auto | Explicit path to `planes_list.txt` |
| `-bin-dir` | `<path>` | `.` | Directory containing executables (`executable_lc`, etc.) |
| `-ini-dir` | `<path>` | auto | Directory containing `.ini` files (supports flat or subfolder layout) |
| `-m`, `--mem` | `<float>` | `4.0` | Memory ceiling in GB per process |
| `-j`, `--joblog`| `<path>` | none | File where GNU Parallel logs exit codes and execution times |
| `-r`, `--results`| `<path>`| none | Directory where stdout and stderr of each job are captured |
| `-f`, `--force` | flag | `false` | Force recomputation even if output files already exist |
| `-h`, `--help` | flag | - | Show help message and exit |

---

## 2. Example Invocations

### Run 16 cores on a workstation:
```bash
./forecast.sh -n 16 -i 0 -m 4.0 -ini-dir /storage/configs -j jobs.log -r logs/
```

### Resume an interrupted run (skips already computed planes):
```bash
./forecast.sh -n 32 -i 0 -ini-dir /storage/configs
```
