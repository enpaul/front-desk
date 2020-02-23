"""Authentication domain meta admin settings model definition

The domain administration settings allow access to be granted to accounts assigned to
the domain to manage the domain itself. This allows accounts to manage the parts of
Keyosk that they need to without granting permissions to every domain Keyosk knows
about.

However, to avoid circular foreign key references, the admin settings need their own
relation tabel. If these settings were part of the main :class:`Domain` model then there
would be circular references between it and the :class:`DomainAccessList` and
:class:`DomainPermission` models.
"""
from typing import Generator
from typing import Tuple

import peewee

from keyosk.database._shared import KeyoskBaseModel
from keyosk.database.domain import Domain
from keyosk.database.domain import DomainAccessList
from keyosk.database.domain import DomainPermission


class DomainAdmin(KeyoskBaseModel):
    """Authentication domain meta administration storage model

    :attribute access_list: The ACL that an account must have permissions for to manage
                            the domain settings
    :attribute domain_read: Permission granted by the ACL entry that gives the assigned
                            account read access to the domain settings
    :attribute domain_update: Permission granted by the ACL entry that gives the
                              assigned account update access to the domain settings
    :attribute account_create: Permission granted by the ACL entry that gives the
                               assigned account access to create new accounts assigned
                               to the domain
    :attribute account_read: Permission granted by the ACL entry that gives the
                             assigned account read access to the accounts assigned to
                             the domain
    :attribute account_delete: Permission granted by the ACL entry that gives the
                               assigned account access to unassign an account from the
                               domain

    There are two permissions not available via this model that may make sense to
    implement in the future: ``account_update`` and ``domain_delete``. The first is not
    implemented due to the potential conflicts it causes: an account can be assigned to
    multiple domains, so granting permissions on one domain to modify an account may
    implicitly grant that same permission on one or more accounts assigned to another
    domain; this seemed ill advised. The second is not implemented for no real good
    reason, other than it seemed out of the inteneded usage of "domain management".

    .. note:: Both the permissions denoted above, as well as other permissions not
              enumerated here, are available through the primary Keyosk authentication
              domain.
    """

    class Meta:  # pylint: disable=missing-docstring,too-few-public-methods
        table_name = "domain_admin"

    domain = peewee.ForeignKeyField(
        Domain, unique=True, null=False, backref="_administration"
    )
    access_list = peewee.ForeignKeyField(DomainAccessList, null=True)
    domain_read = peewee.ForeignKeyField(DomainPermission, null=True)
    domain_update = peewee.ForeignKeyField(DomainPermission, null=True)
    account_create = peewee.ForeignKeyField(DomainPermission, null=True)
    account_read = peewee.ForeignKeyField(DomainPermission, null=True)
    account_delete = peewee.ForeignKeyField(DomainPermission, null=True)

    def __iter__(self) -> Generator[Tuple[str, str], None, None]:
        yield "access_list", self.access_list.name
        yield "domain_read", self.domain_read.name
        yield "account_create", self.account_create.name
        yield "account_read", self.account_read.name
        yield "account_delete", self.account_delete.name
