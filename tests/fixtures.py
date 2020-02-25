import contextlib
import datetime

import _pytest
import passlib.hash
import pytest

from keyosk import config
from keyosk import database
from keyosk.database import Account
from keyosk.database import AccountACLEntry
from keyosk.database import Domain
from keyosk.database import DomainAccessList
from keyosk.database import DomainPermission


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
        Account(
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
        Account(
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
        Account(
            username="hsolo",
            encrypted_client_set_secret=passlib.hash.pbkdf2_sha512.hash("landosux"),
            encrypted_server_set_secret=passlib.hash.pbkdf2_sha512.hash("12ab34cd"),
            enabled=True,
            extras={"full-name": "Han Solo", "homeworld": "Corellia", "jedi": False,},
        ),
        Account(
            username="deusexmachina",
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
        Account(
            username="jack.oneill@airforce.gov",
            encrypted_client_set_secret=passlib.hash.pbkdf2_sha512.hash("topgun"),
            encrypted_server_set_secret=passlib.hash.pbkdf2_sha512.hash("987654321"),
            enabled=True,
            extras={"rank": "colonel", "species": "human",},
        ),
        Account(
            username="tealc@airforce.gov",
            encrypted_client_set_secret=passlib.hash.pbkdf2_sha512.hash(
                "yourloginpassword"
            ),
            encrypted_server_set_secret=passlib.hash.pbkdf2_sha512.hash("abcdefghijk"),
            enabled=True,
            extras={"rank": None, "species": "jaffa"},
        ),
        Account(
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
        Domain(
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
        Domain(
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
            Account.bulk_create(accounts)
            Domain.bulk_create(domains)

        starwars = Domain.get(Domain.name == "star-wars")
        stargate = Domain.get(Domain.name == "stargate")

        access_lists = [
            DomainAccessList(name="imperial-star-destroyer", domain=starwars),
            DomainAccessList(name="millenium-falcon", domain=starwars),
            DomainAccessList(name="x-wing", domain=starwars),
            DomainAccessList(name="nebulon-b", domain=starwars),
            DomainAccessList(name="p90", domain=stargate),
            DomainAccessList(name="staff-weapon", domain=stargate),
            DomainAccessList(name="zatniktel", domain=stargate),
        ]

        permissions = [
            DomainPermission(name="access", bitindex=0, domain=starwars),
            DomainPermission(name="fly", bitindex=1, domain=starwars),
            DomainPermission(name="attack", bitindex=2, domain=starwars),
            DomainPermission(name="own", bitindex=0, domain=stargate),
            DomainPermission(name="fire", bitindex=1, domain=stargate),
            DomainPermission(name="reload", bitindex=2, domain=stargate),
            DomainPermission(name="repair", bitindex=3, domain=stargate),
        ]

        with database.interface.atomic():
            DomainAccessList.bulk_create(access_lists)
            DomainPermission.bulk_create(permissions)

        deusexmachina = Account.get(Account.username == "deusexmachina")
        lskywalker = Account.get(Account.username == "lskywalker")
        jackoneill = Account.get(Account.username == "jack.oneill@airforce.gov")

        sw_isd = DomainAccessList.get(
            DomainAccessList.name == "imperial-star-destroyer"
        )
        sg_zatniktel = DomainAccessList.get(DomainAccessList.name == "zatniktel")

        sw_access = DomainPermission.get(DomainPermission.name == "access")
        sw_fly = DomainPermission.get(DomainPermission.name == "fly")
        sw_attack = DomainPermission.get(DomainPermission.name == "attack")
        sg_own = DomainPermission.get(DomainPermission.name == "own")
        sg_fire = DomainPermission.get(DomainPermission.name == "fire")
        sg_reload = DomainPermission.get(DomainPermission.name == "reload")
        sg_repair = DomainPermission.get(DomainPermission.name == "repair")

        acls = [
            AccountACLEntry(
                account=deusexmachina,
                access_list=sw_isd,
                permission=sw_access,
                with_server_secret=True,
                with_client_secret=False,
            ),
            AccountACLEntry(
                account=deusexmachina,
                access_list=sw_isd,
                permission=sw_fly,
                with_server_secret=True,
                with_client_secret=False,
            ),
            AccountACLEntry(
                account=deusexmachina,
                access_list=sw_isd,
                permission=sw_attack,
                with_server_secret=True,
                with_client_secret=False,
            ),
            AccountACLEntry(
                account=deusexmachina,
                access_list=sg_zatniktel,
                permission=sg_own,
                with_server_secret=True,
                with_client_secret=False,
            ),
            AccountACLEntry(
                account=deusexmachina,
                access_list=sg_zatniktel,
                permission=sg_fire,
                with_server_secret=True,
                with_client_secret=False,
            ),
            AccountACLEntry(
                account=deusexmachina,
                access_list=sg_zatniktel,
                permission=sg_reload,
                with_server_secret=True,
                with_client_secret=False,
            ),
            AccountACLEntry(
                account=deusexmachina,
                access_list=sg_zatniktel,
                permission=sg_repair,
                with_server_secret=True,
                with_client_secret=False,
            ),
            AccountACLEntry(
                account=lskywalker,
                access_list=sw_isd,
                permission=sw_attack,
                with_server_secret=True,
                with_client_secret=True,
            ),
            AccountACLEntry(
                account=lskywalker,
                access_list=sw_isd,
                permission=sw_access,
                with_server_secret=True,
                with_client_secret=False,
            ),
            AccountACLEntry(
                account=jackoneill,
                access_list=sg_zatniktel,
                permission=sg_fire,
                with_server_secret=True,
                with_client_secret=True,
            ),
            AccountACLEntry(
                account=jackoneill,
                access_list=sg_zatniktel,
                permission=sg_reload,
                with_server_secret=True,
                with_client_secret=True,
            ),
            AccountACLEntry(
                account=jackoneill,
                access_list=sg_zatniktel,
                permission=sg_repair,
                with_server_secret=True,
                with_client_secret=False,
            ),
        ]

        with database.interface.atomic():
            AccountACLEntry.bulk_create(acls)

        yield
