"""Test that about module matches pyproject

Currently poetry does not have a way to access meta info about a module/package
at runtime from within the package itself (without installing poetry as a dependency
of every project). To get around this, we could ship the ``pyproject.toml`` along with
the sdist and wheels, which seems clumsy, or we can create the semi-standard
``__about__.py`` and enforce consistency through a test that will let us know if the two
are not equal to each other
"""
from pathlib import Path

import toml

from keyosk import __about__


with Path(".", "pyproject.toml").open() as infile:
    PYPROJECT = toml.load(infile)


def test_version():
    assert __about__.__version__ == PYPROJECT["tool"]["poetry"]["version"]


def test_title():
    assert __about__.__title__ == PYPROJECT["tool"]["poetry"]["name"]
