import peewee

from keyosk.database._shared import KeyoskBaseModel
from keyosk.database.domain import KeyoskDomain


class KeyoskDomainPermission(KeyoskBaseModel):
    class Meta:  # pylint: disable=too-few-public-methods,missing-docstring
        table_name = "domain_permission"

    domain = peewee.ForeignKeyField(
        KeyoskDomain, null=False, on_delete="CASCADE", backref="permissions"
    )
    name = peewee.CharField(null=False)
