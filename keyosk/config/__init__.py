"""Application configuration settings containers and loading functions"""
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Optional
from typing import Union

import marshmallow as msh
import toml

from keyosk import constants
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


def load(source: Optional[Union[str, Path]] = None) -> KeyoskConfig:
    """Load the configuration data

    :param source: Optional path to the configuration file to load

    The configuration file path can be found from one of the three follow places, listed
    in the order of priority:

    1. Parameter passed directly to this function
    2. Environment variable specified by ``constants.ENV_CONFIG_PATH``
    3. The default location, specified by ``constants.DEFAULT_CONFIG_PATH``
    """

    source = Path(
        source or os.getenv(constants.ENV_CONFIG_PATH, constants.DEFAULT_CONFIG_PATH)
    )

    if source.exists():
        with source.open() as infile:
            data = toml.load(infile)
    else:
        data = {}

    return ConfigSerializer().load(data)
