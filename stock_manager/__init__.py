"""
SLAC Inventory Management Application.

This package provides the core application logic and entry points
for the SLAC Inventory Management system, including versioning and
the main application window.
"""
from . import _version
from .app import App

__version__ = _version.get_versions()['version']
__all__ = ['App']
