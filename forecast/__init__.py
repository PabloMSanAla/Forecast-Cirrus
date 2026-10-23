"""
FORECAST - Cosmological Lightcone Synthesis and Postprocessing Pipeline.
"""

__version__ = "1.0.0"
__author__ = "Pablo MSanAla / FORECAST Team"

from . import postprocessing
from .cli import main

__all__ = ["__version__", "postprocessing", "main"]
