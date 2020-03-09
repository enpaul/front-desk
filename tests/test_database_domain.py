import copy
import datetime

import peewee
import pytest
from fixtures import demo_database

from keyosk import database


def test_formatting(demo_database):
    for domain in database.KeyoskDomain.select():
        assert str(domain.uuid) in str(domain)
        assert domain.name in str(domain)


def test_unique(demo_database):
    new_base = database.KeyoskDomain(
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

    starwars = database.KeyoskDomain.get(database.KeyoskDomain.name == "star-wars")

    unique = ["name", "audience"]
    nonunique = ["title", "description", "contact"]

    for item in unique:
        new = copy.deepcopy(new_base)
        setattr(new, item, getattr(starwars, item))
        with pytest.raises(peewee.IntegrityError):
            with database.interface.atomic():
                database.KeyoskDomain.bulk_create([new])

    for item in nonunique:
        new = copy.deepcopy(new_base)
        setattr(new, item, getattr(starwars, item))
        with database.interface.atomic():
            database.KeyoskDomain.bulk_create([new])

        with database.interface.atomic():
            new.delete_instance()


def test_unique_access_lists(demo_database):
    new_base = database.KeyoskDomainAccessList(
        name="imperial-star-destroyer",
        domain=database.KeyoskDomain.get(database.KeyoskDomain.name == "star-wars"),
    )

    isd = database.KeyoskDomainAccessList.get(
        database.KeyoskDomainAccessList.name == "imperial-star-destroyer"
    )

    unique = ["name"]

    for item in unique:
        new = copy.deepcopy(new_base)
        setattr(new, item, getattr(isd, item))
        with pytest.raises(peewee.IntegrityError):
            with database.interface.atomic():
                database.KeyoskDomainAccessList.bulk_create([new])
