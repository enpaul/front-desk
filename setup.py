# pylint: disable=missing-docstring
import os

from setuptools import find_packages
from setuptools import setup

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
ABOUT = {}
with open(os.path.join(BASE_DIR, "front_desk", "__about__.py")) as f:
    exec(f.read(), ABOUT)  # pylint: disable=exec-used


setup(
    name=ABOUT["__title__"],
    version=ABOUT["__version__"],
    description=ABOUT["__summary__"],
    author=ABOUT["__author__"],
    author_email=ABOUT["__author_email__"],
    url=ABOUT["__url__"],
    license=ABOUT["__license__"],
    packages=find_packages(),
    install_requires=[
        "bcrypt>=3.1.6, <4.0.0",
        "flask-restful>=0.3.7, <0.4.0",
        "passlib>=1.7.1, <2.0.0",
        "toml>=0.9.4, <1.0.0",
    ],
)
