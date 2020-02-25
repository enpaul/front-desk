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
from keyosk import datatypes
from keyosk.database._shared import INTERFACE as interface
from keyosk.database._shared import KeyoskBaseModel
from keyosk.database.account import Account
from keyosk.database.domain import Domain
from keyosk.database.mappings import AccountACL
from keyosk.database.mappings import AccountAssignment
from keyosk.database.mappings import DomainAccessList
from keyosk.database.mappings import DomainAdmin
from keyosk.database.mappings import DomainPermission


MODELS: List[Type[KeyoskBaseModel]] = [
    Account,
    Domain,
    DomainAccessList,
    DomainPermission,
    DomainAdmin,
    AccountACL,
    AccountAssignment,
]


def initialize(conf: config.KeyoskConfig):
    """Initialize the database interface

    Defining the database as an
    `unconfigured proxy object <http://docs.peewee-orm.com/en/latest/peewee/database.html#setting-the-database-at-run-time>`_
    allows it to be configured at runtime based on the config values.

    :param config: Populated configuration container object
    """

    logger = logging.getLogger(__name__)

    if conf.storage.backend == datatypes.StorageBackend.SQLITE:
        logger.debug("Using SQLite database backend")
        pragmas = {
            **conf.storage.sqlite.pragmas,
            **{
                "journal_mode": "wal",
                "cache_size": -1 * 64000,
                "foreign_keys": 1,
                "ignore_check_constraints": 0,
                "synchronous": 0,
            },
        }
        for key, value in pragmas:
            logger.debug(f"Applying pragma '{key}' with value '{value}'")
        database = peewee.SqliteDatabase(conf.storage.sqlite.path, pragmas=pragmas)

    elif conf.storage.backend == datatypes.StorageBackend.MARIA:
        logger.debug("Using MariaDB database backend")
        database = peewee.MySQLDatabase(
            conf.storage.maria.schema,
            host=conf.storage.maria.host,
            port=conf.storage.maria.port,
            user=conf.storage.maria.username,
            password=conf.storage.maria.password,
            charset="utf8mb4",
        )
        logger.debug(
            f"Configuring MariaDB: {conf.storage.maria.username}@{conf.storage.maria.host}:{conf.storage.maria.port} `{conf.storage.maria.schema}`"
        )

    interface.initialize(database)

    with interface.atomic():
        interface.create_tables(MODELS)
