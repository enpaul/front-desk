"""Data containers and utilities related to the storage configuration"""
from dataclasses import asdict
from dataclasses import dataclass
from dataclasses import field
from pathlib import Path
from typing import Any
from typing import Dict
from typing import Mapping
from typing import Optional
from typing import Union

import marshmallow as msh

from keyosk import _fields as custom_fields
from keyosk import datatypes


def _default_sqlite_pragmas() -> Dict[str, Any]:
    """Generate the default pragmas for the sqlite connection

    Default are taken from
    `here <http://docs.peewee-orm.com/en/latest/peewee/database.html#recommended-settings>`_
    """
    return {
        "journal_mode": "wal",
        "cache_size": -1 * 64000,
        "foreign_keys": 1,
        "ignore_check_constraints": 0,
        "synchronous": 0,
    }


@dataclass
class KeyoskSQLiteStorageConfig:
    """Config data container for the SQLite config options

    :param path: Path to the SQLite database file
    :param pragmas: Mapping of SQLite pragmas to apply to the database connection
    """

    path: Path = Path("/usr/share/keyosk.db")
    pragmas: Mapping[str, Any] = field(default_factory=_default_sqlite_pragmas)


class SQLiteStorageConfigSerializer(msh.Schema):
    """De/serializer for the SQLite configuration parameters

    Fields on this class map 1:1 with the dataclass parameters on the
    :class:`KeyoskSQLiteStorageConfig` class.
    """

    path = custom_fields.PathString()
    pragmas = msh.fields.Dict(keys=msh.fields.String(), values=msh.fields.Raw())

    # pylint: disable=unused-argument,no-self-use

    @msh.post_load
    def _make_dataclass(self, data: Mapping[str, Any], *args, **kwargs):
        return KeyoskSQLiteStorageConfig(**data)

    @msh.pre_dump
    def _unmake_dataclass(
        self, data: Union[Mapping[str, Any], KeyoskSQLiteStorageConfig], *args, **kwargs
    ):
        if isinstance(data, KeyoskSQLiteStorageConfig):
            return asdict(data)
        return data


@dataclass
class KeyoskMariaStorageConfig:
    """Config data container for the MariaDB config options

    :param schema: Database schema to use
    :param host: IP address or hostname of the database server to connect to
    :param port: Port to connect to the database server on
    :param username: Username for connecting to the database server
    :param password: Password for the user account to use for connecting to the database
                     server

    .. note:: The MySQL driver treats the hosts ``localhost`` and ``127.0.0.1``
              differently: using ``localhost`` will cause the client to always attempt
              to use a socket connection, while ``127.0.0.1`` will cause the client to
              always attempt to use a TCP connection.
    """

    schema: str = "keyosk"
    host: str = "localhost"
    port: int = 3306
    username: str = "keyosk"
    password: Optional[str] = None


class MariaStorageConfigSerializer(msh.Schema):
    """De/serializer for the MariaDB configuration parameters

    Fields on this class map 1:1 with the dataclass parameters on the
    :class:`KeyoskMariaStorageConfig` class.
    """

    schema = msh.fields.String()
    host = msh.fields.String()
    port = msh.fields.Integer(validate=msh.validate.Range(min=1, max=65535))
    username = msh.fields.String()
    password = msh.fields.String(allow_none=True)

    # pylint: disable=unused-argument,no-self-use

    @msh.post_load
    def _make_dataclass(self, data: Mapping[str, Any], *args, **kwargs):
        return KeyoskMariaStorageConfig(**data)

    @msh.pre_dump
    def _unmake_dataclass(
        self, data: Union[Mapping[str, Any], KeyoskMariaStorageConfig], *args, **kwargs
    ):
        if isinstance(data, KeyoskMariaStorageConfig):
            return asdict(data)
        return data


@dataclass
class KeyoskStorageConfig:
    """Config data container for storage related parameters

    :param backend: The backend database system the application should use
    :param sqlite: Configuration parameters for the SQLite backend
    :param maria: Configuration parameters for the MariaDB backend

    .. note:: Only one of the ``sqlite`` or ``maria`` parameters will be used at any one
              time, depending on the value of the ``backend`` setting.
    """

    backend: datatypes.StorageBackend = datatypes.StorageBackend.SQLITE
    sqlite: KeyoskSQLiteStorageConfig = KeyoskSQLiteStorageConfig()
    maria: KeyoskMariaStorageConfig = KeyoskMariaStorageConfig()


class StorageConfigSerializer(msh.Schema):
    """De/serializer for the storage configuration parameters

    Fields on this class map 1:1 with the dataclass parameters on the
    :class:`KeyoskStorageConfig` class.
    """

    backend = custom_fields.EnumItem(datatypes.StorageBackend, pretty_names=True)
    sqlite = msh.fields.Nested(SQLiteStorageConfigSerializer)
    maria = msh.fields.Nested(MariaStorageConfigSerializer)

    # pylint: disable=unused-argument,no-self-use

    @msh.post_load
    def _make_dataclass(self, data: Mapping[str, Any], *args, **kwargs):
        return KeyoskStorageConfig(**data)

    @msh.pre_dump
    def _unmake_dataclass(
        self, data: Union[Mapping[str, Any], KeyoskStorageConfig], *args, **kwargs
    ):
        if isinstance(data, KeyoskStorageConfig):
            return asdict(data)
        return data
