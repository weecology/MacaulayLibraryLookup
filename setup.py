"""Setup script for MacaulayLibraryLookup package."""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="macaulay-library-lookup",
    version="1.0.0",
    author="Weecology",
    author_email="weecology@weecology.org",
    description="A tool for automating Macaulay Library media lookups",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/weecology/MacaulayLibraryLookup",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Scientific/Engineering :: Bio-Informatics",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=6.0",
            "pytest-cov>=2.0",
            "black>=21.0",
            "flake8>=3.8",
            "mypy>=0.910",
            "pre-commit>=2.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "macaulay-lookup=macaulay_library_lookup.cli:main",
        ],
    },
    include_package_data=True,
    zip_safe=False,
)