"""Compatibility imports for the bcbdata client; use bcbdata in new code."""

import importlib as _importlib
import sys as _sys

import bcbdata as _implementation

__all__ = _implementation.__all__
globals().update({name: getattr(_implementation, name) for name in __all__})

# Alias whole modules so legacy patches, exceptions, and pickles use the same objects.
for _name in ("artifacts", "client", "codes", "constants"):
    _module = _importlib.import_module(f"bcbdata.{_name}")
    globals()[_name] = _module
    _sys.modules[f"{__name__}.{_name}"] = _module
