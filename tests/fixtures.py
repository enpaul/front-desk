import contextlib
import datetime

import _pytest
import passlib.hash
import pytest

from keyosk import config
from keyosk import database


@contextlib.contextmanager
def sqlite_database(tmp_path):
    """Database context manager for use with other fixtures that add data"""

    sqlite_path = tmp_path / "test.db"

    conf = config.ConfigSerializer().load(
        {"storage": {"backend": "sqlite", "sqlite": {"path": str(sqlite_path)}}}
    )

    database.initialize(conf)
    yield
    with contextlib.suppress(FileNotFoundError):
        sqlite_path.unlink()


@pytest.fixture(scope="module")
def demo_database(request, tmp_path_factory):
    """Generate a database with test data in it for tests"""
    # The built in tmp_path fixture is function scope so even though we want the ``demo_database``
    # fixture to be module scope it would end up behaving as if it were function scope because the
    # database file path would change for every invocation. Thus this fixture simply rebuilds the
    # tmp_path fixture internally. Relevant source code:
    # https://github.com/pytest-dev/pytest/blob/master/src/_pytest/tmpdir.py#L169
    # pylint: disable=protected-access
    tmp_path = _pytest.tmpdir._mk_tmp(request, tmp_path_factory)

    accounts = [
        database.Account(
            username="lskywalker",
            encrypted_client_set_secret=passlib.hash.pbkdf2_sha512.hash(
                "xWingLuvr4evA"
            ),
            encrypted_server_set_secret=passlib.hash.pbkdf2_sha512.hash("abcd1234"),
            enabled=True,
            extras={
                "full-name": "Luke Skywalker",
                "homeworld": "Polis Massa",
                "jedi": True,
            },
        ),
        database.Account(
            username="dvader",
            encrypted_client_set_secret=passlib.hash.pbkdf2_sha512.hash(
                "nobodyKnowsIKilledAllTheYounglings"
            ),
            encrypted_server_set_secret=passlib.hash.pbkdf2_sha512.hash("1234abcd"),
            enabled=True,
            extras={
                "full-name": "Anikan Skywalker",
                "homeworld": "Tatooine",
                "jedi": False,
            },
        ),
        database.Account(
            username="hsolo",
            encrypted_client_set_secret=passlib.hash.pbkdf2_sha512.hash("landosux"),
            encrypted_server_set_secret=passlib.hash.pbkdf2_sha512.hash("12ab34cd"),
            enabled=True,
            extras={"full-name": "Han Solo", "homeworld": "Corellia", "jedi": False,},
        ),
        database.Account(
            username="dexmachina",
            encrypted_client_set_secret=passlib.hash.pbkdf2_sha512.hash(
                "whenyouneedsomethingtosavetheday:whoyagonnacall"
            ),
            encrypted_server_set_secret=passlib.hash.pbkdf2_sha512.hash("123456789"),
            enabled=True,
            extras={
                "full-name": "Deus Ex Machina",
                "homeworld": None,
                "jedi": False,
                "rank": None,
                "species": None,
            },
        ),
        database.Account(
            username="jack.oneill@airforce.gov",
            encrypted_client_set_secret=passlib.hash.pbkdf2_sha512.hash("topgun"),
            encrypted_server_set_secret=passlib.hash.pbkdf2_sha512.hash("987654321"),
            enabled=True,
            extras={"rank": "colonel", "species": "human",},
        ),
        database.Account(
            username="tealc@airforce.gov",
            encrypted_client_set_secret=passlib.hash.pbkdf2_sha512.hash(
                "yourloginpassword"
            ),
            encrypted_server_set_secret=passlib.hash.pbkdf2_sha512.hash("abcdefghijk"),
            enabled=True,
            extras={"rank": None, "species": "jaffa"},
        ),
        database.Account(
            username="jonas.quinn@airforce.gov",
            encrypted_client_set_secret=passlib.hash.pbkdf2_sha512.hash(
                "d7409ed1dd0a485b8e09f7147ad0e3ab"
            ),
            encrypted_server_set_secret=passlib.hash.pbkdf2_sha512.hash("asdfghjkl"),
            enabled=True,
            extras={"rank": None, "species": "kelownan"},
        ),
    ]

    domains = [
        database.Domain(
            name="star-wars",
            audience="stwr",
            title="Star Wars (by Disney)",
            description="A space opera about space wizards, what's not to like?",
            contact="glucas@disney.com",
            enabled=True,
            enable_client_set_auth=True,
            enable_server_set_auth=True,
            enable_refresh=True,
            lifespan_access=datetime.timedelta(minutes=30),
            lifespan_refresh=datetime.timedelta(days=30),
        ),
        database.Domain(
            name="stargate",
            audience="sg1",
            title="Stargate SG-1",
            description="Quippy, campy, imaginative sci-fi",
            contact="https://sgc.gov/contact",
            enabled=True,
            enable_client_set_auth=False,
            enable_server_set_auth=True,
            enable_refresh=False,
            lifespan_access=datetime.timedelta(minutes=90),
            lifespan_refresh=datetime.timedelta(days=30),
        ),
    ]

    with sqlite_database(tmp_path):
        with database.interface.atomic():
            database.Account.bulk_create(accounts)
            database.Domain.bulk_create(domains)

        starwars = database.Domain.get(database.Domain.name == "star-wars")
        stargate = database.Domain.get(database.Domain.name == "stargate")

        access_lists = [
            database.DomainAccessList(name="imperial-star-destroyer", domain=starwars),
            database.DomainAccessList(name="millenium-falcon", domain=starwars),
            database.DomainAccessList(name="x-wing", domain=starwars),
            database.DomainAccessList(name="nebulon-b", domain=starwars),
            database.DomainAccessList(name="p90", domain=stargate),
            database.DomainAccessList(name="staff-weapon", domain=stargate),
            database.DomainAccessList(name="zatniktel", domain=stargate),
        ]

        permissions = [
            database.DomainPermission(name="access", bitindex=0, domain=starwars),
            database.DomainPermission(name="fly", bitindex=1, domain=starwars),
            database.DomainPermission(name="attack", bitindex=2, domain=starwars),
            database.DomainPermission(name="own", bitindex=0, domain=stargate),
            database.DomainPermission(name="fire", bitindex=1, domain=stargate),
            database.DomainPermission(name="reload", bitindex=2, domain=stargate),
            database.DomainPermission(name="repair", bitindex=3, domain=stargate),
        ]

        with database.interface.atomic():
            database.DomainAccessList.bulk_create(access_lists)
            database.DomainPermission.bulk_create(permissions)

        yield
