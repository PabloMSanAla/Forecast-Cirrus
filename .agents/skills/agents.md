# FORECAST Pipeline Improvement – Multi-Agent System

## Objective
Improve the FORECAST pipeline (C/C++ hydrodynamical simulation processor) by:
1. Making it RAM-aware (never exceed user-specified memory limits). Main change. 
2. Optimizing execution speed while guaranteeing **bit-exact** outputs.
3. Fully documenting all changes and their performance impact.

Only improve the LC and DF modules. Add more effort into the 1. RAM-aware improvements, as it is the main change.

Each executible file should be run by given the pair of snapshot and plane number from the input parameters, then it has to validate the pair by checking the plane number against `planes_list.txt`. As an example, to run this row:

2   0.0175277   35   69.6429   1   98   0.01

it will be by calling, ./executable_df 98 1 .

## The Four Agents

| Agent ID | Role | Primary Skill | Dependency |
| :--- | :--- | :--- | :--- |
| **ram_estimator** | RAM Monitor & Controller | Predicts peak RSS and adapts batch sizes dynamically. | Must run before pipeline execution. |
| **performance_optimizer** | Performance Optimizer | Identifies bottlenecks (I/O, loops) and applies safe, deterministic optimizations. | Works on source code; must be validated by test_validator. |
| **change_tracker** | Documentation & Audit | Logs every decision, code change, and performance delta. | Runs continuously alongside others. |
| **test_validator** | Validation & QA | Runs regression tests, monitors RAM in real-time, and compares outputs byte-for-byte. | Final gatekeeper; must PASS before any merge. |

## Proposed Workflow Sequence
1. **test_validator** → Establish baseline (metrics, MD5 checksums, peak RAM).
2. **ram_estimator** → Analyze input snapshots and adjust `config.ini` thresholds.
3. **performance_optimizer** → Scan `.cpp` files, apply OpenMP and I/O patches.
4. **change_tracker** → Generate changelog and commit changes with impact metrics.
5. **test_validator** (re-run) → Compare optimized outputs against baseline. Enforce RAM limit strictly.

## Success Metrics
- RAM: Peak usage ≤ user-defined limit (tested at 4GB, 8GB, 16GB).
- Speed: ≥ 20% reduction in wall-clock time per module.
- Correctness: 100% MD5 checksum match across all output files.
- Documentation: Every change has a rationale and performance impact attached.
