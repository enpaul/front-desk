import peewee

from keyosk.database._shared import KeyoskBaseModel
from keyosk.database.account import KeyoskAccount
from keyosk.database.domain_access_list import KeyoskDomainAccessList
from keyosk.database.domain_permission import KeyoskDomainPermission


class KeyoskAccountScope(KeyoskBaseModel):
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
        table_name = "account_scope"

    account = peewee.ForeignKeyField(
        KeyoskAccount, null=False, on_delete="CASCADE", backref="scopes"
    )
    access_list = peewee.ForeignKeyField(
        KeyoskDomainAccessList, null=False, on_delete="CASCADE"
    )
    permission = peewee.ForeignKeyField(
        KeyoskDomainPermission, null=False, on_delete="CASCADE"
    )
    with_server_secret = peewee.BooleanField(null=False)
    with_client_secret = peewee.BooleanField(null=False)

    def __str__(self):
        return f"ACL {self.permission.name}@{self.access_list.name} (scope:{'+'.join([item for item in ['server' if self.with_server_secret else '', 'client' if self.with_client_secret else ''] if item])})"
