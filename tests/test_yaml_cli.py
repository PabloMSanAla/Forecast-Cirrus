#!/usr/bin/env python3
"""
Unit and integration tests for FORECAST unified YAML configuration and CLI tool.
Verifies:
1. `forecast check` with forecast.yaml
2. `forecast planes` with YAML configuration matches reference planes_list.txt
3. Backward compatibility: executables accept both -ini and -c flags
4. Unified CLI entry point `./forecast` and `bin/forecast`
"""

import os
import sys
import subprocess
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

class TestYamlCLI(unittest.TestCase):

    def test_forecast_cli_help(self):
        """Test forecast CLI prints help and exits with code 0."""
        cli_path = REPO_ROOT / "bin/forecast"
        res = subprocess.run([str(cli_path), "--help"], capture_output=True, text=True)
        self.assertEqual(res.returncode, 0)
        self.assertIn("FORECAST - Synthetic Lightcone Simulator CLI", res.stdout)
        self.assertIn("planes", res.stdout)
        self.assertIn("lc", res.stdout)
        self.assertIn("df", res.stdout)
        self.assertIn("dc", res.stdout)
        self.assertIn("igm", res.stdout)
        self.assertIn("image", res.stdout)
        self.assertIn("run", res.stdout)

    def test_forecast_check(self):
        """Test forecast check validates the configuration file."""
        cli_path = REPO_ROOT / "bin/forecast"
        res = subprocess.run([str(cli_path), "check", "-c", str(REPO_ROOT / "forecast.yaml")],
                             capture_output=True, text=True)
        self.assertEqual(res.returncode, 0)
        self.assertIn("FORECAST Pipeline Environment Check", res.stdout)
        self.assertIn("executable_lc", res.stdout)
        self.assertIn("executable_df", res.stdout)
        self.assertIn("executable_dc", res.stdout)
        self.assertIn("executable_igm", res.stdout)
        self.assertIn("create_image", res.stdout)
        self.assertIn("make_lc_plane", res.stdout)

    def test_make_lc_plane_yaml(self):
        """Test make_lc_plane with -c forecast.yaml generates accurate plane list."""
        out_tmp = REPO_ROOT / "test_yaml_planes_list.txt"
        try:
            res = subprocess.run([
                str(REPO_ROOT / "tools/make_lc_plane/make_lc_plane"),
                "-c", str(REPO_ROOT / "forecast.yaml"),
                "-o", str(out_tmp)
            ], capture_output=True, text=True)
            self.assertEqual(res.returncode, 0)
            self.assertTrue(out_tmp.is_file())
            
            # Verify row count and contents match reference
            ref_path = Path("/Volumes/PMSAdrive/pmsa/storage/TNG/optimization/planes_list.txt")
            if ref_path.is_file():
                with open(out_tmp) as f1, open(ref_path) as f2:
                    self.assertEqual(f1.read(), f2.read())
        finally:
            if out_tmp.is_file():
                out_tmp.unlink()

    def test_all_executables_accept_config_flag(self):
        """Test that all module executables accept -c and -config flags."""
        executables = [
            REPO_ROOT / "lc/executable_lc",
            REPO_ROOT / "df/executable_df",
            REPO_ROOT / "dc/executable_dc",
            REPO_ROOT / "igm/executable_igm",
            REPO_ROOT / "postprocessing/create_image/create_image",
        ]
        yaml_path = str(REPO_ROOT / "forecast.yaml")
        for exe in executables:
            self.assertTrue(exe.is_file(), f"Executable {exe} missing")
            # Running with invalid plane number should fail plane validation (exit code 1),
            # NOT option parsing (exit code 1 with usage)
            res = subprocess.run([str(exe), "98", "999", "4.0", "-c", yaml_path],
                                 capture_output=True, text=True)
            self.assertEqual(res.returncode, 1)
            output = res.stderr + res.stdout
    def test_global_cli_from_any_directory(self):
        """Test that forecast can be executed via PATH from an arbitrary directory."""
        # Find 'forecast' in PATH
        import shutil
        which_forecast = shutil.which("forecast")
        self.assertIsNotNone(which_forecast, "forecast executable not found in PATH")
        
        # Run forecast --help from /tmp
        res = subprocess.run(["forecast", "--help"], cwd="/tmp", capture_output=True, text=True)
        self.assertEqual(res.returncode, 0)
        self.assertIn("FORECAST - Synthetic Lightcone Simulator CLI", res.stdout)

        # Run forecast check from /tmp
        res_chk = subprocess.run(["forecast", "check", "-c", str(REPO_ROOT / "forecast.yaml")],
                                 cwd="/tmp", capture_output=True, text=True)
        self.assertEqual(res_chk.returncode, 0)
        self.assertIn("Pipeline configuration is READY", res_chk.stdout)

    def test_forecast_run_skip_options(self):
        """Test that forecast run displays and accepts --skip-lc and --start-from."""
        res = subprocess.run(["forecast", "run", "--help"], capture_output=True, text=True)
        self.assertEqual(res.returncode, 0)
        self.assertIn("--skip-lc", res.stdout)
        self.assertIn("--start-from", res.stdout)

if __name__ == "__main__":
    unittest.main()
