from dataclasses import dataclass

import marshmallow as msh

from keyosk.config.storage import KeyoskStorageConfig
from keyosk.config.storage import StorageConfigSerializer


@dataclass
class KeyoskConfig:
    """Configuration storage"""

    storage: KeyoskStorageConfig = KeyoskStorageConfig()


class ConfigSerializer(msh.Schema):
    """De/serializer for the application configuration

    Fields on this class map 1:1 with the dataclass parameters on the
    :class:`KeyoskConfig` class.
    """

    storage = msh.fields.Nested(StorageConfigSerializer)
