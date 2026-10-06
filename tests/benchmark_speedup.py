#!/usr/bin/env python3
"""
benchmark_speedup.py - Measure single-core wall-clock time and verify >=20% speedup.

Authoritative Reference:
  - ORIGINAL_REQUEST.md: Execution wall-clock time reduced by at least 20% compared to baseline on test planes.
    No internal threading/OpenMP added inside lc and df modules.
  - PROJECT.md: Target >= 20% speedup (F3: LC speedup, F7: DF speedup).
"""

import argparse
import csv
import datetime
import json
import os
import shlex
import subprocess
import sys
import time
from pathlib import Path
from typing import Dict, List, Optional, Tuple

# Pre-recorded standard baseline times (seconds) for Snapshot 98 test planes on development host
# These serve as fallback reference baselines when live baseline binary is not provided.
REFERENCE_BASELINE_TIMES: Dict[str, Dict[str, float]] = {
    "lc": {
        "0": 0.50,    # Plane 0: Small test slice (~10 KB coords)
        "1": 3.20,    # Plane 1: Medium test slice (~450 KB coords)
        "3": 28.50,   # Plane 3: Large test slice (~17.9 MB coords)
    },
    "df": {
        "0": 0.80,    # Plane 0: Small test slice (~1.2 KB flux)
        "1": 6.50,    # Plane 1: Medium test slice (~539 KB flux)
        "3": 65.00,   # Plane 3: Large test slice (~21.8 MB flux)
    },
}


def normalize_cmd(cmd_list: List[str]) -> List[str]:
    """Expand single quoted command string or return token list."""
    if len(cmd_list) == 1 and " " in cmd_list[0]:
        return shlex.split(cmd_list[0])
    return cmd_list


def run_command(cmd: List[str], verbose: bool = False) -> Tuple[int, float, str, str]:
    """Execute command and return (exit_code, duration_seconds, stdout, stderr)."""
    if verbose:
        print(f"[INFO] Running: {' '.join(cmd)}")
    start = time.perf_counter()
    proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    duration = time.perf_counter() - start
    return proc.returncode, duration, proc.stdout, proc.stderr


def run_benchmark_iterations(
    cmd: List[str], repeats: int = 1, verbose: bool = False
) -> Tuple[int, float, List[float], str, str]:
    """Execute command multiple times and return minimum/median duration."""
    timings = []
    last_stdout, last_stderr = "", ""
    ret = 0

    for i in range(repeats):
        ret, duration, stdout, stderr = run_command(cmd, verbose=verbose)
        last_stdout = stdout
        last_stderr = stderr
        if ret != 0:
            return ret, duration, timings, stdout, stderr
        timings.append(duration)

    best_time = min(timings) if timings else 0.0
    return ret, best_time, timings, last_stdout, last_stderr


def main():
    parser = argparse.ArgumentParser(
        description="Benchmark single-core wall-clock time and verify >=20% speedup against baseline."
    )
    parser.add_argument(
        "--opt-cmd",
        type=str,
        default=None,
        help="Command string to run optimized binary (e.g. --opt-cmd './lc/executable_lc 98 0')",
    )
    parser.add_argument(
        "--base-cmd",
        type=str,
        default=None,
        help="Command string to run baseline binary for live comparison (e.g. --base-cmd './lc/executable_lc_base 98 0')",
    )
    parser.add_argument(
        "--baseline-time",
        type=float,
        default=None,
        help="Explicit baseline execution time in seconds",
    )
    parser.add_argument(
        "--module",
        choices=["lc", "df"],
        default=None,
        help="Module name (lc or df) for reference baseline lookup",
    )
    parser.add_argument(
        "--plane",
        type=str,
        default=None,
        help="Plane index (0, 1, or 3) for reference baseline lookup",
    )
    parser.add_argument(
        "--min-speedup-pct",
        type=float,
        default=20.0,
        help="Minimum required speedup percentage (default: 20.0%%)",
    )
    parser.add_argument(
        "--repeats",
        type=int,
        default=1,
        help="Number of iterations to run (takes minimum duration, default: 1)",
    )
    parser.add_argument(
        "--append-csv",
        type=Path,
        default=None,
        help="Append benchmark metrics to CSV file (e.g. docs/performance_history.csv)",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output results in JSON format",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Print verbose execution details and subprocess output",
    )
    parser.add_argument(
        "command",
        nargs=argparse.REMAINDER,
        help="Positional optimized command if --opt-cmd is omitted (prefix with '--')",
    )

    args = parser.parse_args()

    # Resolve optimized command
    opt_cmd = None
    if args.opt_cmd:
        opt_cmd = shlex.split(args.opt_cmd)
    elif args.command:
        cmd_args = args.command
        if cmd_args and cmd_args[0] == "--":
            cmd_args = cmd_args[1:]
        opt_cmd = normalize_cmd(cmd_args)

    if not opt_cmd:
        print("[ERROR] No target command specified to benchmark.", file=sys.stderr)
        parser.print_help(file=sys.stderr)
        sys.exit(1)

    # Determine baseline time
    base_time = args.baseline_time
    if args.base_cmd:
        base_cmd_list = shlex.split(args.base_cmd)
        print(f"[INFO] Benchmarking live baseline: {' '.join(base_cmd_list)}")
        ret_b, base_time, _, out_b, err_b = run_benchmark_iterations(
            base_cmd_list, repeats=args.repeats, verbose=args.verbose
        )
        if ret_b != 0:
            print(f"[FAIL] Baseline execution failed with exit code {ret_b}", file=sys.stderr)
            if err_b:
                print(err_b, file=sys.stderr)
            sys.exit(ret_b)
    elif base_time is None:
        # Check if module and plane can be inferred from command or arguments
        mod = args.module
        plane = args.plane
        if not mod:
            for piece in opt_cmd:
                if "lc" in piece.lower():
                    mod = "lc"
                    break
                elif "df" in piece.lower():
                    mod = "df"
                    break
        if not plane:
            for piece in opt_cmd:
                if piece in ["0", "1", "3"]:
                    plane = piece
                    break

        if mod and plane and mod in REFERENCE_BASELINE_TIMES and plane in REFERENCE_BASELINE_TIMES[mod]:
            base_time = REFERENCE_BASELINE_TIMES[mod][plane]
            print(f"[INFO] Using reference baseline time for {mod.upper()} plane {plane}: {base_time:.3f} s")
        else:
            print(
                "[ERROR] No baseline time provided. Specify --baseline-time, --base-cmd, or --module and --plane.",
                file=sys.stderr,
            )
            sys.exit(1)

    print(f"[INFO] Benchmarking optimized target: {' '.join(opt_cmd)}")
    ret_opt, opt_time, timings, out_opt, err_opt = run_benchmark_iterations(
        opt_cmd, repeats=args.repeats, verbose=args.verbose
    )

    if ret_opt != 0:
        print(f"[FAIL] Optimized target exited with code {ret_opt}", file=sys.stderr)
        if err_opt:
            print(err_opt, file=sys.stderr)
        sys.exit(ret_opt)

    # Calculate speedup percentage: ((T_base - T_opt) / T_base) * 100
    speedup_pct = ((base_time - opt_time) / base_time) * 100.0 if base_time > 0 else 0.0
    passed = speedup_pct >= args.min_speedup_pct

    result = {
        "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "optimized_command": " ".join(opt_cmd),
        "baseline_time_sec": round(base_time, 4),
        "optimized_time_sec": round(opt_time, 4),
        "speedup_pct": round(speedup_pct, 2),
        "min_required_pct": args.min_speedup_pct,
        "target_met": passed,
        "timings": [round(t, 4) for t in timings],
    }

    if args.append_csv:
        file_exists = args.append_csv.exists()
        fieldnames = [
            "timestamp",
            "agent_name",
            "module",
            "snapshot",
            "plane",
            "optimized_command",
            "baseline_time_sec",
            "optimized_time_sec",
            "speedup_pct",
            "min_required_pct",
            "passed",
        ]
        with open(args.append_csv, "a", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            if not file_exists:
                writer.writeheader()
            writer.writerow({
                "timestamp": result["timestamp"],
                "agent_name": "benchmark_speedup",
                "module": args.module or "unknown",
                "snapshot": "98",
                "plane": args.plane or "unknown",
                "optimized_command": result["optimized_command"],
                "baseline_time_sec": result["baseline_time_sec"],
                "optimized_time_sec": result["optimized_time_sec"],
                "speedup_pct": result["speedup_pct"],
                "min_required_pct": result["min_required_pct"],
                "passed": passed,
            })

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print("=" * 70)
        print(" FORECAST SINGLE-CORE SPEEDUP BENCHMARK")
        print("=" * 70)
        print(f"Target Command:   {result['optimized_command']}")
        print(f"Baseline Time:    {base_time:.4f} s")
        print(f"Optimized Time:   {opt_time:.4f} s")
        delta_s = base_time - opt_time
        print(f"Time Delta:       {delta_s:+.4f} s")
        status_label = "PASS (Target Met)" if passed else "FAIL (Below Target)"
        print(f"Measured Speedup: {speedup_pct:+.2f}%  (Required: >= {args.min_speedup_pct:.1f}%)")
        print(f"Status:           {status_label}")
        print("=" * 70)

        if args.verbose and out_opt:
            print("\n[OPTIMIZED STDOUT]:\n" + out_opt)

    sys.exit(0 if passed else 1)


if __name__ == "__main__":
    main()
