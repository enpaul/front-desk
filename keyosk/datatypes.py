"""Shared types, enums, and data containers"""
import enum
from typing import Dict
from typing import Union


Extras = Dict[str, Union[int, float, bool, str, None]]


TokenClaims = Dict[str, Union[str, int, bool, Dict[str, int]]]


@enum.unique
class StorageBackend(enum.Enum):
    """Supported storage backends"""

    SQLITE = "sqlite"
    MARIA = "maria"
