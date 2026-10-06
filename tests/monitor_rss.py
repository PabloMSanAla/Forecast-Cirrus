#!/usr/bin/env python3
"""
monitor_rss.py - Real-time peak RSS memory monitor and ceiling enforcer.

Authoritative Reference:
  - ORIGINAL_REQUEST.md: Primary focus: strictly RAM-aware (never exceeding user-defined memory limits
    such as 4GB, 8GB, and 16GB). Zero OOM crashes.
  - PROJECT.md: Darwin-aware RSS checks (ru_maxrss in bytes on macOS vs KB on Linux).
    Exit code 3 on memory ceiling exceeded.
"""

import argparse
import csv
import datetime
import json
import os
import resource
import subprocess
import sys
import time
from pathlib import Path
from typing import List, Optional, Tuple


def get_rusage_mb() -> float:
    """
    Get peak RSS from resource.getrusage(resource.RUSAGE_CHILDREN) converted to MB.
    macOS (Darwin) reports ru_maxrss in BYTES (1024*1024 bytes per MB).
    Linux reports ru_maxrss in KILOBYTES (1024 KB per MB).
    """
    usage = resource.getrusage(resource.RUSAGE_CHILDREN)
    if sys.platform == "darwin":
        return usage.ru_maxrss / (1024.0 * 1024.0)
    else:
        return usage.ru_maxrss / 1024.0


def poll_pid_rss_mb(pid: int) -> Optional[float]:
    """
    Poll process RSS via ps -o rss= -p <pid>.
    Both macOS and Linux ps return RSS in kilobytes.
    """
    try:
        out = subprocess.check_output(
            ["ps", "-o", "rss=", "-p", str(pid)],
            stderr=subprocess.DEVNULL,
        )
        val = out.decode().strip()
        if val:
            return int(val) / 1024.0
    except (subprocess.CalledProcessError, ValueError):
        pass
    return None


def execute_and_monitor(
    command: List[str],
    ceiling_gb: float,
    poll_interval: float = 0.05,
    kill_on_breach: bool = False,
    verbose: bool = False,
) -> dict:
    """
    Execute command, sampling RSS during execution and inspecting child rusage after termination.
    Returns metrics dictionary.
    """
    ceiling_mb = ceiling_gb * 1024.0
    start_time = time.perf_counter()

    if verbose:
        print(f"[INFO] Executing: {' '.join(command)}")
        print(f"[INFO] Memory Ceiling: {ceiling_gb:.2f} GB ({ceiling_mb:.2f} MB)")
        print(f"[INFO] Platform: {sys.platform} (Darwin-aware byte scaling active)")

    proc = subprocess.Popen(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )

    peak_sampled_mb = 0.0
    breached = False

    while proc.poll() is None:
        rss = poll_pid_rss_mb(proc.pid)
        if rss is not None:
            if rss > peak_sampled_mb:
                peak_sampled_mb = rss
            if peak_sampled_mb > ceiling_mb:
                breached = True
                if kill_on_breach:
                    proc.kill()
                    break
        time.sleep(poll_interval)

    stdout, stderr = proc.communicate()
    duration = time.perf_counter() - start_time
    rusage_mb = get_rusage_mb()
    peak_rss_mb = max(peak_sampled_mb, rusage_mb)

    within_ceiling = (peak_rss_mb <= ceiling_mb) and not breached

    result = {
        "command": " ".join(command),
        "exit_code": proc.returncode,
        "ceiling_gb": ceiling_gb,
        "ceiling_mb": ceiling_mb,
        "peak_rss_mb": round(peak_rss_mb, 2),
        "ps_sampled_peak_mb": round(peak_sampled_mb, 2),
        "rusage_peak_mb": round(rusage_mb, 2),
        "duration_sec": round(duration, 3),
        "within_ceiling": within_ceiling,
        "stdout": stdout,
        "stderr": stderr,
    }

    return result


def append_to_performance_csv(csv_path: Path, result: dict, agent_name: str = "test_writer"):
    """Append benchmark run to CSV log."""
    file_exists = csv_path.exists()
    fieldnames = [
        "timestamp",
        "agent_name",
        "command",
        "memory_ceiling_gb",
        "peak_rss_mb",
        "rss_under_ceiling",
        "wall_clock_sec",
        "exit_code",
    ]
    with open(csv_path, "a", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        if not file_exists:
            writer.writeheader()
        writer.writerow({
            "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
            "agent_name": agent_name,
            "command": result["command"],
            "memory_ceiling_gb": result["ceiling_gb"],
            "peak_rss_mb": result["peak_rss_mb"],
            "rss_under_ceiling": result["within_ceiling"],
            "wall_clock_sec": result["duration_sec"],
            "exit_code": result["exit_code"],
        })


def main():
    parser = argparse.ArgumentParser(
        description="Monitor peak RSS of a target command and enforce memory limits (Darwin-aware)."
    )
    parser.add_argument(
        "--ceiling-gb",
        type=float,
        default=4.0,
        help="Memory ceiling in Gigabytes (e.g. 4.0, 8.0, 16.0). Default: 4.0",
    )
    parser.add_argument(
        "--poll-interval",
        type=float,
        default=0.05,
        help="Polling interval in seconds for ps sampling (default: 0.05s / 50ms)",
    )
    parser.add_argument(
        "--kill-on-breach",
        action="store_true",
        help="Immediately terminate process if memory ceiling is breached during execution",
    )
    parser.add_argument(
        "--append-csv",
        type=Path,
        default=None,
        help="Path to CSV file to append performance log",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Print command stdout/stderr and debug information",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Print machine-readable JSON metrics",
    )
    parser.add_argument(
        "command",
        nargs=argparse.REMAINDER,
        help="Command and arguments to execute. Use '--' before command if passing flags.",
    )

    args = parser.parse_args()

    cmd = args.command
    if cmd and cmd[0] == "--":
        cmd = cmd[1:]

    if not cmd:
        print("[ERROR] No command specified to run.", file=sys.stderr)
        parser.print_help(file=sys.stderr)
        sys.exit(1)

    result = execute_and_monitor(
        command=cmd,
        ceiling_gb=args.ceiling_gb,
        poll_interval=args.poll_interval,
        kill_on_breach=args.kill_on_breach,
        verbose=args.verbose,
    )

    if args.append_csv:
        append_to_performance_csv(args.append_csv, result)

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print("=" * 70)
        print(" FORECAST MEMORY & RSS MONITOR (DARWIN-AWARE)")
        print("=" * 70)
        print(f"Command:        {result['command']}")
        print(f"Exit Code:      {result['exit_code']}")
        print(f"Wall-Clock:     {result['duration_sec']:.3f} s")
        print(f"Peak RSS:       {result['peak_rss_mb']:.2f} MB ({result['peak_rss_mb']/1024.0:.3f} GB)")
        print(f"Ceiling:        {result['ceiling_mb']:.2f} MB ({result['ceiling_gb']} GB)")
        status_str = "PASS (Within Limit)" if result["within_ceiling"] else "FAIL (Ceiling Breached)"
        print(f"Ceiling Status: {status_str}")
        print("=" * 70)

        if args.verbose or result["exit_code"] != 0:
            if result["stdout"]:
                print("\n[STDOUT]:\n" + result["stdout"])
            if result["stderr"]:
                print("\n[STDERR]:\n" + result["stderr"])

    if not result["within_ceiling"]:
        print(
            f"[FAIL] Memory ceiling violated! Peak RSS ({result['peak_rss_mb']:.2f} MB) "
            f"exceeded ceiling ({result['ceiling_mb']:.2f} MB)",
            file=sys.stderr,
        )
        sys.exit(3)  # Interface contract exit code 3: Memory ceiling exceeded

    if result["exit_code"] != 0:
        print(f"[FAIL] Command failed with exit code {result['exit_code']}", file=sys.stderr)
        sys.exit(result["exit_code"])

    sys.exit(0)


if __name__ == "__main__":
    main()
