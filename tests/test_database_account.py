import peewee
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
