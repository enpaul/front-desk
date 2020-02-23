"""Shared types, enums, and data containers"""
import enum
from typing import Dict
from typing import Union


Extras = Dict[str, Union[int, float, bool, str, None]]


class TokenUsage(enum.Enum):
    """Possible usage values for an issued JWT

    Values will be the value of the ``ksk-usg`` claim in the issued token
    """

    REFRESH = "ref"
    ACCESS = "acc"


@enum.unique
class StorageBackend(enum.Enum):
    """Supported storage backends"""

    SQLITE = "sqlite"
    MARIA = "maria"
