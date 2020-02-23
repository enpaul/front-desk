from pathlib import Path

import toml

from keyosk import __about__


PYPROJECT_PATH = Path("pyproject.toml")


def test_version():
    with PYPROJECT_PATH.open() as infile:
        pyproject = toml.load(infile)

    assert __about__.__version__ == pyproject["tool"]["poetry"]["version"]


def test_title():
    with PYPROJECT_PATH.open() as infile:
        pyproject = toml.load(infile)

    assert __about__.__title__ == pyproject["tool"]["poetry"]["name"]
