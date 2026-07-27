"""Standard setuptools build entry point for the enterprise-lite wheel.

The upstream project intentionally blocks generic wheels because its public
installer depends on a source-checkout/Nix asset layout.  This downstream build
ships only the retained Python runtime and uses standard package metadata from
pyproject.toml so it can be mirrored in an internal package index.
"""

from setuptools import setup

setup()
