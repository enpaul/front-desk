import copy

import passlib
import peewee
import pytest
from fixtures import demo_database

from keyosk import database


def test_meta():
    for key in database.Account.dict_keys():
        assert hasattr(database.Account, key)
        attr = getattr(database.Account, key)

        if key in database.Account.foreign_ref():
            assert isinstance(attr, peewee.ForeignKeyField)
        else:
            assert not isinstance(attr, peewee.ForeignKeyField)

        if key in database.Account.foreign_backref():
            assert isinstance(attr, peewee.BackrefAccessor)
        else:
            assert not isinstance(attr, peewee.BackrefAccessor)


def test_formatting(demo_database):
    for account in database.Account.select():
        assert list(dict(account).keys()) == database.Account.dict_keys()
        assert str(account.uuid) in str(account)
        assert account.username in str(account)


def test_extras(demo_database):
    account = database.Account.get(database.Account.username == "lskywalker")

    new_extras = {"foo": "bar", "fizz": "buzz", "baz": False, "blop": 1234.567}

    account.extras = new_extras
    with database.interface.atomic():
        account.save()

    account = database.Account.get(database.Account.username == "lskywalker")
    assert account.extras == new_extras


def test_crypto(demo_database):
    account = database.Account.get(
        database.Account.username == "jack.oneill@airforce.gov"
    )

    account.update_client_set_secret("oneillWithTwoLs")
    with database.interface.atomic():
        account.save()
    account = database.Account.get(
        database.Account.username == "jack.oneill@airforce.gov"
    )
    assert account.verify_client_set_secret("oneillWithTwoLs")

    new_autopass = account.update_server_set_secret()
    with database.interface.atomic():
        account.save()
    account = database.Account.get(
        database.Account.username == "jack.oneill@airforce.gov"
    )
    assert account.verify_server_set_secret(new_autopass)


def test_unique(demo_database):
    new_base = database.Account(
        username="garbage",
        encrypted_client_set_secret=passlib.hash.pbkdf2_sha512.hash("garbage"),
        encrypted_server_set_secret=passlib.hash.pbkdf2_sha512.hash("garbage"),
        enabled=True,
        extras={"gar": "bage"},
    )

    vader = database.Account.get(database.Account.username == "dvader")

    unique = ["username"]
    nonunique = ["extras"]

    for item in unique:
        new = copy.deepcopy(new_base)
        setattr(new, item, getattr(vader, item))
        # Using bulk create as a hacky work around for a weird issue. When using numeric
        # TIDs peewee apparently raises an integrity error when calling ``save()``,
        # however when using UUID TIDs it just returns 0 (for the number of edited rows)
        # The second is the behavior as documented, but I want the integrity error. I
        # don't care enough to figure out why its behaving differently here, and bulk
        # create gives me that integrity error I'm after
        with pytest.raises(peewee.IntegrityError):
            with database.interface.atomic():
                database.Account.bulk_create([new])

    for item in nonunique:
        new = copy.deepcopy(new_base)
        setattr(new, item, getattr(vader, item))
        with database.interface.atomic():
            database.Account.bulk_create([new])

        with database.interface.atomic():
            new.delete_instance()
