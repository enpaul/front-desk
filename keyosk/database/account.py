"""Authentication account model definition"""
import datetime
import json

import peewee

from keyosk.database._shared import KeyoskBaseModel
from keyosk.database.domain import KeyoskDomainAccessList
from keyosk.database.domain import KeyoskDomainPermission
from keyosk.datatypes import Extras


class KeyoskAccount(KeyoskBaseModel):
    """Authentication account storage model

    :attribute created: Datetime indicating when the account was first created
    :attribute updated: Datetime indicating when the account was last modified
    :attribute username: Account authentication identity
    :attribute encrypted_client_set_secret: Client-provided account authentication
                                            secret
    :attribute encrypted_server_set_secret: Server-provided account authentication
                                            secret
    :attribute enabled: Whether the account is enabled for authentication
    :property extras: Key/value pairs of arbitrary additional infomration for the
                      account
    """

    class Meta:  # pylint: disable=missing-docstring,too-few-public-methods
        table_name = "account"

    created = peewee.DateTimeField(null=False, default=datetime.datetime.utcnow)
    updated = peewee.DateTimeField(null=False, default=datetime.datetime.utcnow)
    username = peewee.CharField(null=False, unique=True)
    encrypted_client_set_secret = peewee.CharField(null=False)
    encrypted_server_set_secret = peewee.CharField(null=False)
    enabled = peewee.BooleanField(null=False)
    _extras = peewee.CharField(null=False, default="{}")

    @property
    def extras(self) -> Extras:
        """Return the loaded extras dictionary"""
        return json.loads(self._extras)

    @extras.setter
    def extras(self, value: Extras):
        """Set the extras dictionary"""
        self._extras = json.dumps(value)

    def __str__(self) -> str:
        return f"Account '{self.username}' ({self.uuid})"


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
