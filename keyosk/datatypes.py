import enum
from typing import Dict
from typing import Union


Extras = Dict[str, Union[int, float, bool, str, None]]


class TokenUsage(enum.Enum):
    REFRESH = enum.auto()
    ACCESS = enum.auto()


@enum.unique
class StorageBackend(enum.Enum):
    SQLITE = "sqlite"
    MARIA = "maria"
