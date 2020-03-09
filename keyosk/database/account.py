"""Authentication account model definition"""
import datetime
import json

import peewee

from keyosk.database._shared import KeyoskBaseModel
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
