"""Account access control list entry model definition

Access Control Lists (ACLs) are entities that can have permissions assigned to them
under certain conditions. Permissions are the possible permissions that can be granted-
or not granted- to an ACL. An entry in an ACL comprises the ACL identifier, the
permission to grant, and the identity that should be granted the permission.
"""
import peewee

from keyosk.database._shared import KeyoskBaseModel
from keyosk.database.account import Account
from keyosk.database.domain import DomainAccessList
from keyosk.database.domain import DomainPermission


class AccountACLEntry(KeyoskBaseModel):
    """Access control list entry model definition

    :attribute account: Account the ACL entry applies to
    :attribute access_list: The access list the entry is for
    :attribute permission: The permission the entry is for
    :attribute with_server_secret: Whether the permission should be applied when the
                                   account authenticates with the account's
                                   server-set-secret
    :attribute with_client_secret: Whether the permission should be applied when the
                                   account authenticates with the account's
                                   client-set-secret

    .. note:: Since permissions are by definition boolean, there is no need to store a
              value parameter with an ACL entry: if an entry exists for a given account
              for a given access list with a given permission, then that permission is
              granted on that access list to that account; similarly, if one does not
              exist then it is not granted.
    """

    class Meta:  # pylint: disable=missing-docstring,too-few-public-methods
        table_name = "account_acl"

    account = peewee.ForeignKeyField(Account, backref="acls")
    access_list = peewee.ForeignKeyField(DomainAccessList)
    permission = peewee.ForeignKeyField(DomainPermission)
    with_server_secret = peewee.BooleanField(null=False)
    with_client_secret = peewee.BooleanField(null=False)

    def __iter__(self):
        yield "access_list", self.access_list.name
        yield "permission", self.permission.name
        yield "with_server_secret", self.with_server_secret
        yield "with_client_secret", self.with_client_secret

    def __str__(self):
        return f"ACL {self.permission.name}@{self.access_list.name} (scope:{'+'.join([item for item in ['server' if self.with_server_secret else '', 'client' if self.with_client_secret else ''] if item])})"
