"""Authentication account model definition"""
import datetime
import json
import secrets
from typing import List

import passlib.hash
import peewee

from keyosk.database._shared import KeyoskBaseModel
from keyosk.database.domain import Domain
from keyosk.datatypes import Extras


class Account(KeyoskBaseModel):
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

    def verify_client_set_secret(self, value: str) -> bool:
        """Verify the client set secret matches a value

        :param value: The string to check matches the client-set-secret
        :returns: Boolean indicating whether the provided value matches the encrypted
                  secret
        """
        return passlib.hash.pbkdf2_sha512.verify(
            value, self.encrypted_client_set_secret
        )

    def verify_server_set_secret(self, value: str) -> bool:
        """Verify the server set secret matches a value

        :param value: The string to check matches the server-set-secret
        :returns: Boolean indicating whether the provided value matches the encrypted
                  secret
        """
        return passlib.hash.pbkdf2_sha512.verify(
            value, self.encrypted_server_set_secret
        )

    def update_client_set_secret(self, value: str) -> None:
        """Update the client set secret

        :param value: The string to set the encrypted client-set-secret to
        """
        self.encrypted_client_set_secret = passlib.hash.pbkdf2_sha512.hash(value)

    def update_server_set_secret(self, length: int = 42) -> str:
        """Update the server set secret

        :param length: Optional length of the generated token
        :returns: The new value of the server set secret
        """
        value = secrets.token_urlsafe(length)
        self.encrypted_server_set_secret = passlib.hash.pbkdf2_sha512.hash(value)
        return value

    @staticmethod
    def dict_keys() -> List[str]:
        return ["uuid", "created", "updated", "username", "enabled", "extras"]
