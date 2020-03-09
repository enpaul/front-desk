# pylint: disable=unused-argument,redefined-outer-name,unused-import
import copy

import passlib
import peewee
import pytest
from fixtures import demo_database

from keyosk import database


def test_formatting(demo_database):
    for account in database.KeyoskAccount.select():
        assert str(account.uuid) in str(account)
        assert account.username in str(account)


def test_extras(demo_database):
    account = database.KeyoskAccount.get(
        database.KeyoskAccount.username == "lskywalker"
    )

    new_extras = {"foo": "bar", "fizz": "buzz", "baz": False, "blop": 1234.567}

    account.extras = new_extras
    with database.interface.atomic():
        account.save()

    account = database.KeyoskAccount.get(
        database.KeyoskAccount.username == "lskywalker"
    )
    assert account.extras == new_extras


def test_unique(demo_database):
    new_base = database.KeyoskAccount(
        username="garbage",
        encrypted_client_set_secret=passlib.hash.pbkdf2_sha512.hash("garbage"),
        encrypted_server_set_secret=passlib.hash.pbkdf2_sha512.hash("garbage"),
        enabled=True,
        extras={"gar": "bage"},
    )

    vader = database.KeyoskAccount.get(database.KeyoskAccount.username == "dvader")

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
                database.KeyoskAccount.bulk_create([new])

    for item in nonunique:
        new = copy.deepcopy(new_base)
        setattr(new, item, getattr(vader, item))
        with database.interface.atomic():
            database.KeyoskAccount.bulk_create([new])

        with database.interface.atomic():
            new.delete_instance()
