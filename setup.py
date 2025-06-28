#!/usr/bin/env python3
"""Setup script for PyCEFRizer."""

from setuptools import setup, find_packages

# Read the contents of README file
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="pycefrizer",
    version="3.0.0",
    author="PyCEFRizer Contributors",
    description="PyCEFRizer - CEFR-J Level Estimator for analyzing English text difficulty",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/straygizmo/PyCEFRizer",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Education",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Text Processing :: Linguistic",
        "Topic :: Education",
    ],
    python_requires=">=3.9",
    install_requires=[
        "spacy>=3.7.2",
        "textstat>=0.7.4",
        "nltk>=3.8",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0",
            "pytest-cov>=4.0",
            "black>=23.0",
            "ruff>=0.1.0",
        ],
    },
    package_data={
        "pycefrizer": ["data/*.json"],
    },
    include_package_data=True,
    entry_points={
        "console_scripts": [
            "pycefrizer=pycefrizer.cli:main",
        ],
    },
)