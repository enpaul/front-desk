import peewee
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
