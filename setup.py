#!/usr/bin/env python3
"""Setup script for SeismoWatch."""

from setuptools import setup, find_packages
import os

# Read README for long description
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

# Read requirements
with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="seismowatch",
    version="1.0.0",
    author="SeismoWatch Contributors",
    author_email="info@seismowatch.com",
    description="Real-time earthquake monitoring platform with alerts and visualizations",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/seismowatch/seismowatch",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Science/Research",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Scientific/Engineering :: GIS",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
        "Topic :: System :: Monitoring",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "pytest-mock>=3.10.0",
            "black>=22.0.0",
            "flake8>=4.0.0",
            "mypy>=0.991",
            "pre-commit>=2.20.0",
        ],
        "docs": [
            "sphinx>=4.0.0",
            "sphinx-rtd-theme>=1.0.0",
            "myst-parser>=0.18.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "seismowatch=seismowatch.cli:main",
        ],
    },
    include_package_data=True,
    package_data={
        "seismowatch": ["templates/*.html", "static/*"],
    },
    keywords="earthquake, seismic, monitoring, alerts, visualization, geospatial, usgs",
    project_urls={
        "Bug Reports": "https://github.com/seismowatch/seismowatch/issues",
        "Source": "https://github.com/seismowatch/seismowatch",
        "Documentation": "https://seismowatch.readthedocs.io/",
        "Demo": "https://seismowatch.github.io/",
    },
)