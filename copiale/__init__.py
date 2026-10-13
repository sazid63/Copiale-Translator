"""Copiale cipher translator (verified historical key + approved extensions)."""
from .translate import encode, decode, render, CopialeError
from . import key

__all__ = ["encode", "decode", "render", "CopialeError", "key"]
__version__ = "0.1.0"
