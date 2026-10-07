from setuptools import setup

setup(
    name="forecast-sim",
    version="1.0.0",
    description="FORECAST - Cosmological Lightcone Synthesis Pipeline CLI",
    scripts=["bin/forecast"],
    install_requires=["pyyaml>=5.1"],
)
