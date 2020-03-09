"""Access token model definition"""
import datetime
import json

import peewee

from keyosk import datatypes
from keyosk.database._shared import KeyoskBaseModel
from keyosk.database.account import KeyoskAccount
from keyosk.database.domain import KeyoskDomain


class Token(KeyoskBaseModel):
    """Issued access token storage model

    :attribute account: Account the token was issued to
    :attribute domain: Domain the token was issued for
    :attribute issuer: Value of the issuer parameter at generation time
    :attribute issued: Datetime indicating when the token was issued
    :attribute expires: Datetime indicating when the token expires
    :attribute revoked: Whether the token has been revoked
    :attribute refresh: Refresh token attached to the issued access token; can be
                        ``None`` if refresh tokens are disabled for the domain
    :attribute refresh_expires: Datetime indicating when the refresh token, if used,
                                expires
    :property claims: Claims generated for the token

    .. note:: Settings and parameters may be changed on linked records. However, the
              ``claims`` property will always contain the set of claims as assigned at
              issuance time.
    """

    class Meta:  # pylint: disable=missing-docstring,too-few-public-methods
        table_name = "token"

    account = peewee.ForeignKeyField(
        KeyoskAccount, backref="tokens", null=True, on_delete="SET NULL"
    )
    domain = peewee.ForeignKeyField(
        KeyoskDomain, backref="tokens", null=True, on_delete="SET NULL"
    )
    issuer = peewee.CharField(null=False)
    issued = peewee.DateTimeField(null=False, default=datetime.datetime.utcnow)
    expires = peewee.DateTimeField(null=False)
    revoked = peewee.BooleanField(null=False)
    refresh = peewee.CharField(null=True)
    refresh_expires = peewee.DateTimeField(null=True)
    hash_publickey = peewee.CharField(null=False)
    hash_blacklist = peewee.CharField(null=False)
    _scopes = peewee.CharField(null=False, default="[]")

    @property
    def scopes(self) -> datatypes.TokenClaims:
        """Return the claims dictionary"""
        return json.loads(self._scopes)

    @scopes.setter
    def scopes(self, value: datatypes.TokenClaims):
        """Set the claims dictionary"""
        self._scopes = json.dumps(value)
