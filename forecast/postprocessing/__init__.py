"""
FORECAST Postprocessing Library.
Provides modular astronomical image stacking and galaxy catalog compilation tools.
"""

from .sum_images import sum_massive_fits, sum_massive_fits_fast
from .sum_fits import stack_fits_images
from .galaxy_cat import build_galaxy_catalog
from .merge_cat import merge_galaxy_catalogs

__all__ = [
    "sum_massive_fits",
    "sum_massive_fits_fast",
    "stack_fits_images",
    "build_galaxy_catalog",
    "merge_galaxy_catalogs",
]
