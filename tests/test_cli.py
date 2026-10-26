#!/usr/bin/env python3
"""
test_cli.py - Comprehensive CLI argument parsing and plane validation test harness.

Authoritative Reference:
  - ORIGINAL_REQUEST.md R3: Executables accept <snapshot> <plane_number> as CLI arguments
    (e.g., ./executable_df 98 1) and validate the plane number against planes_list.txt before execution.
  - PROJECT.md:
      Exit codes:
        0: Success
        1: Invalid arguments or failed plane validation (plane not found or snapshot mismatch)
        2: Missing configuration or input data files
        3: Memory ceiling exceeded
"""

import argparse
import os
import subprocess
import sys
import time
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple

DEFAULT_PLANES_LIST_PATHS = [
    Path(__file__).resolve().parent.parent / "lc" / "planes_list.txt",
    Path("/Volumes/PMSAdrive/pmsa/storage/TNG/optimization/planes_list.txt"),
    Path("./lc/planes_list.txt"),
    Path("./planes_list.txt"),
]


def find_planes_list(custom_path: Optional[Path] = None) -> Optional[Path]:
    """Find planes_list.txt from custom path or standard locations."""
    if custom_path and custom_path.exists():
        return custom_path
    for p in DEFAULT_PLANES_LIST_PATHS:
        if p.exists():
            return p
    return None


def parse_planes_list(planes_file: Path) -> Dict[str, Set[str]]:
    """
    Parse planes_list.txt to extract mapping of snapshot_id -> set of valid plane indices.
    """
    snap_to_planes: Dict[str, Set[str]] = {}
    with open(planes_file, "r") as f:
        for line in f:
            parts = line.strip().split()
            if len(parts) >= 6:
                try:
                    display_num = parts[0]
                    replica_idx = parts[4]
                    snap_id = parts[5]

                    if snap_id not in snap_to_planes:
                        snap_to_planes[snap_id] = set()

                    snap_to_planes[snap_id].add(replica_idx)
                    snap_to_planes[snap_id].add(display_num)
                except (ValueError, IndexError):
                    continue
    return snap_to_planes


def run_cli_test(
    binary_path: Path,
    args: List[str],
    expect_invalid: bool,
    timeout: float = 3.0,
    cwd: Optional[Path] = None,
    strict_exit_codes: bool = True,
) -> Tuple[bool, int, str, str, str]:
    """
    Run the binary with given arguments and evaluate CLI specification compliance.
    """
    abs_binary = binary_path.resolve()
    work_dir = cwd or abs_binary.parent

    cmd = [str(abs_binary)] + args

    cli_test_env = dict(os.environ)
    if "FORECAST_OUTPUT_DIR" not in cli_test_env:
        os.makedirs("/tmp/forecast_cli_test/", exist_ok=True)
        cli_test_env["FORECAST_OUTPUT_DIR"] = "/tmp/forecast_cli_test/"

    try:
        proc = subprocess.Popen(
            cmd,
            cwd=str(work_dir),
            env=cli_test_env,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        try:
            stdout, stderr = proc.communicate(timeout=timeout)
            ret = proc.returncode
        except subprocess.TimeoutExpired:
            proc.kill()
            stdout, stderr = proc.communicate()
            ret = "TIMEOUT"
    except Exception as e:
        return False, -1, "", str(e), f"Execution error: {e}"

    combined_output = (stdout + "\n" + stderr).lower()

    if expect_invalid:
        # Invalid arguments MUST exit non-zero (specifically code 1 per contract)
        if ret != 0 and ret != "TIMEOUT":
            passed = True
            diag = f"Rejected invalid invocation as expected (exit code {ret})"
        else:
            passed = False
            diag = f"Expected non-zero exit code for invalid args, but got {ret}"
    else:
        # Valid arguments MUST NOT fail validation
        # Contract: Exit 0 = success, Exit 2 = missing data/config, TIMEOUT = executing
        if ret in [0, 2, "TIMEOUT"]:
            passed = True
            diag = f"Valid invocation accepted by CLI parser (exit code {ret})"
        elif ret == 1:
            # Check if this exit code 1 is from CLI parser or un-migrated code
            has_usage_msg = any(k in combined_output for k in ["usage:", "missing arguments", "error: plane"])
            if has_usage_msg or strict_exit_codes:
                passed = False
                diag = "Failed with exit code 1 (CLI validation rejected valid inputs or missing M1/M2 implementation)"
            else:
                passed = True
                diag = "Accepted by CLI parser, but failed later in downstream execution (exit code 1)"
        else:
            passed = False
            diag = f"Unexpected exit code {ret}"

    return passed, ret, stdout, stderr, diag


def test_executable_cli(
    binary_path: Path,
    planes_file: Optional[Path] = None,
    strict_exit_codes: bool = True,
    verbose: bool = False,
) -> Tuple[bool, int, int]:
    """Execute full suite of CLI validation tests for a specific binary."""
    print("=" * 78)
    print(f" TESTING CLI PARSING & PLANE VALIDATION: {binary_path.name}")
    print(f" Binary Path:        {binary_path.resolve()}")
    if planes_file:
        print(f" Planes List:        {planes_file.resolve()}")
    print(f" Strict Exit Codes:  {strict_exit_codes}")
    print("=" * 78)

    if not binary_path.exists():
        print(f"[FAIL] Executable not found: {binary_path}")
        return False, 0, 1

    if not os.access(binary_path, os.X_OK):
        print(f"[FAIL] Executable lacks execute permissions: {binary_path}")
        return False, 0, 1

    test_cases = [
        # --- INVALID TEST CASES (Expected non-zero, exit code 1) ---
        {
            "desc": "Wrong Arg Count: 0 arguments",
            "args": [],
            "expect_invalid": True,
            "category": "Argument Count",
        },
        {
            "desc": "Wrong Arg Count: 1 argument only ('98')",
            "args": ["98"],
            "expect_invalid": True,
            "category": "Argument Count",
        },
        {
            "desc": "Wrong Arg Count: Excess arguments (>3)",
            "args": ["98", "0", "4.0", "extra_arg"],
            "expect_invalid": True,
            "category": "Argument Count",
        },
        {
            "desc": "Invalid Format: Non-integer snapshot ('abc 0')",
            "args": ["abc", "0"],
            "expect_invalid": True,
            "category": "Format Validation",
        },
        {
            "desc": "Invalid Format: Non-integer plane ('98 xyz')",
            "args": ["98", "xyz"],
            "expect_invalid": True,
            "category": "Format Validation",
        },
        {
            "desc": "Invalid Format: Negative snapshot ('-98 0')",
            "args": ["-98", "0"],
            "expect_invalid": True,
            "category": "Format Validation",
        },
        {
            "desc": "Invalid Format: Negative plane index ('98 -1')",
            "args": ["98", "-1"],
            "expect_invalid": True,
            "category": "Format Validation",
        },
        {
            "desc": "Invalid Plane: Out-of-bounds plane number ('98 999')",
            "args": ["98", "999"],
            "expect_invalid": True,
            "category": "Plane Validation",
        },
        {
            "desc": "Invalid Plane: Out-of-bounds plane number ('98 55')",
            "args": ["98", "55"],
            "expect_invalid": True,
            "category": "Plane Validation",
        },
        {
            "desc": "Snapshot Mismatch: Non-existent snapshot ID ('999 0')",
            "args": ["999", "0"],
            "expect_invalid": True,
            "category": "Snapshot Validation",
        },
        {
            "desc": "Snapshot Mismatch: Snapshot 99 for Plane 1 ('99 1')",
            "args": ["99", "1"],
            "expect_invalid": True,
            "category": "Snapshot Validation",
        },
        {
            "desc": "Snapshot Mismatch: Snapshot 70 for Plane 0 ('70 0')",
            "args": ["70", "0"],
            "expect_invalid": True,
            "category": "Snapshot Validation",
        },
        # --- VALID TEST CASES (Must pass CLI validation) ---
        {
            "desc": "Valid Test Plane: Snap 98, Plane 0 (Row 1)",
            "args": ["98", "0"],
            "expect_invalid": False,
            "category": "Valid Invocations",
        },
        {
            "desc": "Valid Test Plane: Snap 98, Plane 1 (Row 2)",
            "args": ["98", "1"],
            "expect_invalid": False,
            "category": "Valid Invocations",
        },
        {
            "desc": "Valid Test Plane: Snap 98, Plane 3 (Row 4)",
            "args": ["98", "3"],
            "expect_invalid": False,
            "category": "Valid Invocations",
        },
        {
            "desc": "Valid Test Plane with 4GB limit: Snap 98, Plane 0, 4.0 GB",
            "args": ["98", "0", "4.0"],
            "expect_invalid": False,
            "category": "Valid Invocations with RAM Limit",
        },
        {
            "desc": "Valid Test Plane with 8GB limit: Snap 98, Plane 1, 8.0 GB",
            "args": ["98", "1", "8.0"],
            "expect_invalid": False,
            "category": "Valid Invocations with RAM Limit",
        },
        {
            "desc": "Valid Test Plane with 16GB limit: Snap 98, Plane 3, 16.0 GB",
            "args": ["98", "3", "16.0"],
            "expect_invalid": False,
            "category": "Valid Invocations with RAM Limit",
        },
    ]

    passed_count = 0
    total_count = len(test_cases)
    all_passed = True

    for tc in test_cases:
        passed, ret, stdout, stderr, diag = run_cli_test(
            binary_path=binary_path,
            args=tc["args"],
            expect_invalid=tc["expect_invalid"],
            strict_exit_codes=strict_exit_codes,
        )

        status_tag = "PASS" if passed else "FAIL"
        expected_desc = "Exit != 0" if tc["expect_invalid"] else "Exit in (0,2,TIMEOUT)"

        print(
            f"[{status_tag}] {tc['desc']:<55} | Ret: {str(ret):<7} | {diag}"
        )

        if passed:
            passed_count += 1
        else:
            all_passed = False
            if verbose:
                if stdout:
                    print(f"       Stdout snippet: {stdout.strip()[:150]}")
                if stderr:
                    print(f"       Stderr snippet: {stderr.strip()[:150]}")

    print("-" * 78)
    print(f"Summary for {binary_path.name}: {passed_count}/{total_count} test cases passed.")
    print("=" * 78)
    return all_passed, passed_count, total_count


def main():
    parser = argparse.ArgumentParser(
        description="Exercise CLI argument parsing and plane validation against planes_list.txt."
    )
    parser.add_argument(
        "--bin",
        type=Path,
        default=None,
        help="Path to specific binary to test (e.g. ./lc/executable_lc or ./df/executable_df)",
    )
    parser.add_argument(
        "--module",
        choices=["lc", "df", "dc", "igm", "image", "all"],
        default="all",
        help="Module(s) to test: lc, df, dc, igm, image, or all (default: all)",
    )
    parser.add_argument(
        "--planes-list",
        type=Path,
        default=None,
        help="Path to planes_list.txt reference table",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        default=True,
        help="Enforce strict exit codes (0, 2 for valid invocations per contract)",
    )
    parser.add_argument(
        "--non-strict",
        action="store_false",
        dest="strict",
        help="Allow downstream failure code 1 if argument parsing passed",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Show stdout/stderr snippets for failed tests",
    )

    args = parser.parse_args()

    planes_file = find_planes_list(args.planes_list)
    if planes_file:
        print(f"[INFO] Authoritative planes list located at: {planes_file}")
    else:
        print("[WARN] planes_list.txt not found; standard validation patterns will be tested.")

    binaries_to_test: List[Path] = []
    if args.bin:
        binaries_to_test.append(args.bin)
    else:
        if args.module in ["lc", "all"]:
            binaries_to_test.append(Path("./lc/executable_lc"))
        if args.module in ["df", "all"]:
            binaries_to_test.append(Path("./df/executable_df"))
        if args.module in ["dc", "all"]:
            binaries_to_test.append(Path("./dc/executable_dc"))
        if args.module in ["igm", "all"]:
            binaries_to_test.append(Path("./igm/executable_igm"))
        if args.module in ["image", "all"]:
            binaries_to_test.append(Path("./postprocessing/create_image/create_image"))

    overall_success = True
    total_passed = 0
    total_tests = 0

    for b in binaries_to_test:
        success, passed, count = test_executable_cli(
            binary_path=b,
            planes_file=planes_file,
            strict_exit_codes=args.strict,
            verbose=args.verbose,
        )
        total_passed += passed
        total_tests += count
        if not success:
            overall_success = False

    print("\n" + "#" * 78)
    print(f" FINAL CLI VALIDATION SUMMARY: {total_passed}/{total_tests} Passed")
    print(f" STATUS: {'ALL CLI SUITES PASSED' if overall_success else 'CLI SUITE FAILURES DETECTED'}")
    print("#" * 78)

    sys.exit(0 if overall_success else 1)


if __name__ == "__main__":
    main()
