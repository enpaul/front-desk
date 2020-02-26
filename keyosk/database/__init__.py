"""Database interface and tooling module

Keyosk uses the
`Peewee Object Relational Model <http://docs.peewee-orm.com/en/latest/peewee/quickstart.html>`_
Python library for its database interface. The database interface object is available as the
``interface`` variable under the ``keyosk.database`` namespace. The individual models (a.k.a.
database tables) are available in the same namespace.

The database connection can be accessed using the
`Peewee atomic transaction context manager <http://docs.peewee-orm.com/en/latest/peewee/database.html#context-manager>`_.
Similarly, the ORM models- which correspond to database tables- can be accessed in the same way:

::

  from keyosk import database

  with database.interface.atomic():
      database.Account.get(username == "atticusfinch")
"""
import logging
from typing import List
from typing import Type

import peewee

from keyosk import config
from keyosk.database._shared import INTERFACE as interface
from keyosk.database._shared import KeyoskBaseModel
from keyosk.database.account import Account
from keyosk.database.account_acl import AccountACLEntry
from keyosk.database.domain import Domain
from keyosk.database.domain import DomainAccessList
from keyosk.database.domain import DomainPermission
from keyosk.database.token import Token


MODELS: List[Type[KeyoskBaseModel]] = [
    Account,
    DomainAccessList,
    DomainPermission,
    Domain,
    AccountACLEntry,
    Token,
]


def initialize(conf: config.KeyoskConfig):
    """Initialize the database interface

    Defining the database as an
    `unconfigured proxy object <http://docs.peewee-orm.com/en/latest/peewee/database.html#setting-the-database-at-run-time>`_
    allows it to be configured at runtime based on the config values.

    :param config: Populated configuration container object
    """

    logger = logging.getLogger(__name__)

    if conf.storage.backend == config.StorageBackend.SQLITE:
        logger.debug("Using SQLite database backend")
        logger.debug(f"Applying SQLite pragmas: {conf.storage.sqlite.pragmas}")
        # Explicit cast-to-string on the path is to support py3.6: sqlite driver
        # requires a string, vs 3.7+ requires a string-like object
        database = peewee.SqliteDatabase(
            str(conf.storage.sqlite.path), pragmas=conf.storage.sqlite.pragmas
        )

    elif conf.storage.backend == config.StorageBackend.MARIA:
        logger.debug("Using MariaDB database backend")
        logger.debug(
            f"Configuring MariaDB: {conf.storage.maria.username}@{conf.storage.maria.host}:{conf.storage.maria.port}, with database '{conf.storage.maria.schema}'"
        )
        database = peewee.MySQLDatabase(
            conf.storage.maria.schema,
            host=conf.storage.maria.host,
            port=conf.storage.maria.port,
            user=conf.storage.maria.username,
            password=conf.storage.maria.password,
            charset="utf8mb4",
        )

    else:
        raise ValueError(
            f"Invalid storage backend in configuration: {conf.storage.backend}"
        )

    interface.initialize(database)

    with interface.atomic():
        interface.create_tables(MODELS)
