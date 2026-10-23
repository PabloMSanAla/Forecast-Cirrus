#!/usr/bin/env python3
"""
Unit tests for FORECAST Python library and forecast.postprocessing subpackage.
"""

import unittest


class TestForecastPostprocessing(unittest.TestCase):

    def test_import_forecast(self):
        """Test top-level package imports and exports."""
        import forecast
        self.assertEqual(forecast.__version__, "1.0.0")
        self.assertTrue(hasattr(forecast, "postprocessing"))
        self.assertTrue(hasattr(forecast, "main"))

    def test_import_postprocessing_functions(self):
        """Test importing core postprocessing tools."""
        from forecast.postprocessing import (
            sum_massive_fits,
            sum_massive_fits_fast,
            stack_fits_images,
            build_galaxy_catalog,
            merge_galaxy_catalogs,
        )
        self.assertTrue(callable(sum_massive_fits))
        self.assertTrue(callable(sum_massive_fits_fast))
        self.assertTrue(callable(stack_fits_images))
        self.assertTrue(callable(build_galaxy_catalog))
        self.assertTrue(callable(merge_galaxy_catalogs))


if __name__ == "__main__":
    unittest.main()
