"""
SLAC Inventory Management Application.

This package provides the core application logic and entry points
for the SLAC Inventory Management system, including versioning and
the main application window.
"""

from . import controllers, model, utils
from ._version import get_versions

__version__ = get_versions()['version']
__all__ = ['App'] + controllers.__all__ + model.__all__ + utils.__all__
