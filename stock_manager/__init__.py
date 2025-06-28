"""Package description here"""
from . import _version
from .app import App

__version__ = _version.get_versions()['version']
__all__ = ['App']
