"""
FORECAST - Cosmological Lightcone Synthesis and Postprocessing Pipeline.
"""

__version__ = "1.0.0"
__author__ = "Pablo MSanAla / FORECAST Team"

from .cli import main

try:
    from . import postprocessing
    __all__ = ["__version__", "postprocessing", "main"]
except ImportError:
    __all__ = ["__version__", "main"]
