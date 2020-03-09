import peewee

from keyosk.database._shared import KeyoskBaseModel
from keyosk.database.domain import KeyoskDomain


class KeyoskDomainAccessList(KeyoskBaseModel):
    class Meta:  # pylint: disable=too-few-public-methods,missing-docstring
        table_name = "domain_access_list"

    domain = peewee.ForeignKeyField(
        KeyoskDomain, null=False, on_delete="CASCADE", backref="access_lists"
    )
    name = peewee.CharField(null=False, unique=True)
