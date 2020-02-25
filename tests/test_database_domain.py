import copy
import datetime

import peewee
import pytest
from fixtures import demo_database

from keyosk import database


def test_meta():
    models = [database.Domain, database.DomainAccessList, database.DomainPermission]
    for model in models:
        for key in model.dict_keys():
            assert hasattr(model, key)
            attr = getattr(model, key)

            if key in model.foreign_ref():
                assert isinstance(attr, peewee.ForeignKeyField)
            else:
                assert not isinstance(attr, peewee.ForeignKeyField)

            if key in model.foreign_backref():
                assert isinstance(attr, peewee.BackrefAccessor)
            else:
                assert not isinstance(attr, peewee.BackrefAccessor)


def test_formatting(demo_database):
    for domain in database.Domain.select():
        assert list(dict(domain).keys()) == database.Domain.dict_keys()
        assert str(domain.uuid) in str(domain)
        assert domain.name in str(domain)

    for permission in database.DomainPermission.select():
        assert list(dict(permission).keys()) == database.DomainPermission.dict_keys()
        assert str(permission.uuid) not in str(permission)

    for access_list in database.DomainAccessList.select():
        assert list(dict(access_list).keys()) == database.DomainAccessList.dict_keys()
        assert str(access_list.uuid) not in str(access_list)


def test_unique(demo_database):
    new_base = database.Domain(
        name="garbage",
        audience="garbage",
        title="garbage",
        description="garbage",
        contact="garbage",
        enabled=True,
        enable_client_set_auth=True,
        enable_server_set_auth=True,
        enable_refresh=True,
        lifespan_access=datetime.timedelta(minutes=30),
        lifespan_refresh=datetime.timedelta(days=30),
    )

    starwars = database.Domain.get(database.Domain.name == "star-wars")

    unique = ["name", "audience"]
    nonunique = ["title", "description", "contact"]

    for item in unique:
        new = copy.deepcopy(new_base)
        setattr(new, item, getattr(starwars, item))
        with pytest.raises(peewee.IntegrityError):
            with database.interface.atomic():
                database.Domain.bulk_create([new])

    for item in nonunique:
        new = copy.deepcopy(new_base)
        setattr(new, item, getattr(starwars, item))
        with database.interface.atomic():
            database.Domain.bulk_create([new])

        with database.interface.atomic():
            new.delete_instance()


def test_unique_access_lists(demo_database):
    new_base = database.DomainAccessList(
        name="imperial-star-destroyer",
        domain=database.Domain.get(database.Domain.name == "star-wars"),
    )

    isd = database.DomainAccessList.get(
        database.DomainAccessList.name == "imperial-star-destroyer"
    )

    unique = ["name"]

    for item in unique:
        new = copy.deepcopy(new_base)
        setattr(new, item, getattr(isd, item))
        with pytest.raises(peewee.IntegrityError):
            with database.interface.atomic():
                database.DomainAccessList.bulk_create([new])
