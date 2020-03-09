import contextlib
import datetime

import passlib.hash
import pytest
import _pytest  # noreorder

from keyosk import config
from keyosk import database
from keyosk.database import KeyoskAccount
from keyosk.database import KeyoskAccountScope
from keyosk.database import KeyoskDomain
from keyosk.database import KeyoskDomainAccessList
from keyosk.database import KeyoskDomainPermission


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


# pylint: disable=too-many-locals
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
        KeyoskAccount(
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
        KeyoskAccount(
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
        KeyoskAccount(
            username="hsolo",
            encrypted_client_set_secret=passlib.hash.pbkdf2_sha512.hash("landosux"),
            encrypted_server_set_secret=passlib.hash.pbkdf2_sha512.hash("12ab34cd"),
            enabled=True,
            extras={"full-name": "Han Solo", "homeworld": "Corellia", "jedi": False,},
        ),
        KeyoskAccount(
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
        KeyoskAccount(
            username="jack.oneill@airforce.gov",
            encrypted_client_set_secret=passlib.hash.pbkdf2_sha512.hash("topgun"),
            encrypted_server_set_secret=passlib.hash.pbkdf2_sha512.hash("987654321"),
            enabled=True,
            extras={"rank": "colonel", "species": "human",},
        ),
        KeyoskAccount(
            username="tealc@airforce.gov",
            encrypted_client_set_secret=passlib.hash.pbkdf2_sha512.hash(
                "yourloginpassword"
            ),
            encrypted_server_set_secret=passlib.hash.pbkdf2_sha512.hash("abcdefghijk"),
            enabled=True,
            extras={"rank": None, "species": "jaffa"},
        ),
        KeyoskAccount(
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
        KeyoskDomain(
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
        KeyoskDomain(
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
            KeyoskAccount.bulk_create(accounts)
            KeyoskDomain.bulk_create(domains)

        starwars = KeyoskDomain.get(KeyoskDomain.name == "star-wars")
        stargate = KeyoskDomain.get(KeyoskDomain.name == "stargate")

        access_lists = [
            KeyoskDomainAccessList(name="imperial-star-destroyer", domain=starwars),
            KeyoskDomainAccessList(name="millenium-falcon", domain=starwars),
            KeyoskDomainAccessList(name="x-wing", domain=starwars),
            KeyoskDomainAccessList(name="nebulon-b", domain=starwars),
            KeyoskDomainAccessList(name="p90", domain=stargate),
            KeyoskDomainAccessList(name="staff-weapon", domain=stargate),
            KeyoskDomainAccessList(name="zatniktel", domain=stargate),
        ]

        permissions = [
            KeyoskDomainPermission(name="access", bitindex=0, domain=starwars),
            KeyoskDomainPermission(name="fly", bitindex=1, domain=starwars),
            KeyoskDomainPermission(name="attack", bitindex=2, domain=starwars),
            KeyoskDomainPermission(name="own", bitindex=0, domain=stargate),
            KeyoskDomainPermission(name="fire", bitindex=1, domain=stargate),
            KeyoskDomainPermission(name="reload", bitindex=2, domain=stargate),
            KeyoskDomainPermission(name="repair", bitindex=3, domain=stargate),
        ]

        with database.interface.atomic():
            KeyoskDomainAccessList.bulk_create(access_lists)
            KeyoskDomainPermission.bulk_create(permissions)

        deusexmachina = KeyoskAccount.get(KeyoskAccount.username == "deusexmachina")
        lskywalker = KeyoskAccount.get(KeyoskAccount.username == "lskywalker")
        jackoneill = KeyoskAccount.get(
            KeyoskAccount.username == "jack.oneill@airforce.gov"
        )

        sw_isd = KeyoskDomainAccessList.get(
            KeyoskDomainAccessList.name == "imperial-star-destroyer"
        )
        sg_zatniktel = KeyoskDomainAccessList.get(
            KeyoskDomainAccessList.name == "zatniktel"
        )

        sw_access = KeyoskDomainPermission.get(KeyoskDomainPermission.name == "access")
        sw_fly = KeyoskDomainPermission.get(KeyoskDomainPermission.name == "fly")
        sw_attack = KeyoskDomainPermission.get(KeyoskDomainPermission.name == "attack")
        sg_own = KeyoskDomainPermission.get(KeyoskDomainPermission.name == "own")
        sg_fire = KeyoskDomainPermission.get(KeyoskDomainPermission.name == "fire")
        sg_reload = KeyoskDomainPermission.get(KeyoskDomainPermission.name == "reload")
        sg_repair = KeyoskDomainPermission.get(KeyoskDomainPermission.name == "repair")

        acls = [
            KeyoskAccountScope(
                account=deusexmachina,
                access_list=sw_isd,
                permission=sw_access,
                with_server_secret=True,
                with_client_secret=False,
            ),
            KeyoskAccountScope(
                account=deusexmachina,
                access_list=sw_isd,
                permission=sw_fly,
                with_server_secret=True,
                with_client_secret=False,
            ),
            KeyoskAccountScope(
                account=deusexmachina,
                access_list=sw_isd,
                permission=sw_attack,
                with_server_secret=True,
                with_client_secret=False,
            ),
            KeyoskAccountScope(
                account=deusexmachina,
                access_list=sg_zatniktel,
                permission=sg_own,
                with_server_secret=True,
                with_client_secret=False,
            ),
            KeyoskAccountScope(
                account=deusexmachina,
                access_list=sg_zatniktel,
                permission=sg_fire,
                with_server_secret=True,
                with_client_secret=False,
            ),
            KeyoskAccountScope(
                account=deusexmachina,
                access_list=sg_zatniktel,
                permission=sg_reload,
                with_server_secret=True,
                with_client_secret=False,
            ),
            KeyoskAccountScope(
                account=deusexmachina,
                access_list=sg_zatniktel,
                permission=sg_repair,
                with_server_secret=True,
                with_client_secret=False,
            ),
            KeyoskAccountScope(
                account=lskywalker,
                access_list=sw_isd,
                permission=sw_attack,
                with_server_secret=True,
                with_client_secret=True,
            ),
            KeyoskAccountScope(
                account=lskywalker,
                access_list=sw_isd,
                permission=sw_access,
                with_server_secret=True,
                with_client_secret=False,
            ),
            KeyoskAccountScope(
                account=jackoneill,
                access_list=sg_zatniktel,
                permission=sg_fire,
                with_server_secret=True,
                with_client_secret=True,
            ),
            KeyoskAccountScope(
                account=jackoneill,
                access_list=sg_zatniktel,
                permission=sg_reload,
                with_server_secret=True,
                with_client_secret=True,
            ),
            KeyoskAccountScope(
                account=jackoneill,
                access_list=sg_zatniktel,
                permission=sg_repair,
                with_server_secret=True,
                with_client_secret=False,
            ),
        ]

        with database.interface.atomic():
            KeyoskAccountScope.bulk_create(acls)

        yield
