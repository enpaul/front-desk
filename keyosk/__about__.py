"""Access package info programatically without duplication"""
import importlib.resources

import toml

PYPROJECT = toml.loads(importlib.resources.read_text("keyosk", "pyproject.toml"))

__authors__ = PYPROJECT["tool"]["poetry"]["authors"]
__summary__ = PYPROJECT["tool"]["poetry"]["description"]
__title__ = PYPROJECT["tool"]["poetry"]["name"]
__url__ = PYPROJECT["tool"]["poetry"]["repository"]
__version__ = PYPROJECT["tool"]["poetry"]["version"]
