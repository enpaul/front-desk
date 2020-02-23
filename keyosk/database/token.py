"""Access token model definition"""
import datetime
import json
import secrets
from collections import OrderedDict
from typing import Sequence

import peewee

from keyosk import datatypes
from keyosk.database._shared import KeyoskBaseModel
from keyosk.database.account import Account
from keyosk.database.account_acl import AccountACLEntry
from keyosk.database.domain import Domain


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
    :property claims: Claims generated for the token

    .. note:: Settings and parameters may be changed on linked records. However, the
              ``claims`` property will always contain the set of claims as assigned at
              issuance time.
    """

    class Meta:  # pylint: disable=missing-docstring,too-few-public-methods
        table_name = "token"

    account = peewee.ForeignKeyField(Account, backref="tokens", null=True)
    domain = peewee.ForeignKeyField(Domain, backref="tokens", null=True)
    issuer = peewee.CharField(null=False)
    issued = peewee.DateTimeField(null=False, default=datetime.datetime.utcnow)
    expires = peewee.DateTimeField(null=False)
    revoked = peewee.BooleanField(null=False)
    refresh = peewee.CharField(null=True)
    _claims = peewee.CharField(null=False)

    @property
    def claims(self) -> datatypes.TokenClaims:
        """Return the claims dictionary"""
        return json.loads(self._claims)

    @claims.setter
    def claims(self, value: datatypes.TokenClaims):
        """Set the claims dictionary"""
        self._claims = json.dumps(value)

    def make_public_claims(self):
        """Generate the public JWT claims from current state data"""
        return {
            "jti": self.uuid,
            "sub": self.account.username,
            "aud": self.domain.audience,
            "iss": self.issuer,
            "exp": int(self.expires.timestamp()),  # pylint: disable=no-member
            "iat": int(self.issued.timestamp()),  # pylint: disable=no-member
        }

    @classmethod
    def factory(
        cls,
        account: Account,
        domain: Domain,
        issuer: str,
        lifespan: datetime.timedelta,
        permissions: Sequence[AccountACLEntry],
        generate_refresh: bool,
    ):
        """Create a new token using provided data

        This function is intentionally not documented, as I expect it will not survive
        first contact with a practical implementation
        """
        new = cls(
            account=account,
            domain=domain,
            issuer=issuer,
            expires=(datetime.datetime.utcnow() + lifespan),
            revoked=False,
            refresh=secrets.token_urlsafe(42) if generate_refresh else None,
        )

        acls = {}
        for permission in permissions:
            # Note: Because we're relying on dictionary order here, we need to use
            # ordered dict to support python3.6. Dictionaries remembering insertion
            # order was officially implemented in 3.6, but not guaranteed until 3.7. So,
            # technically, it would be fine to use a plain'ol'dictionary here, but to
            # conform to best practices we use ordered dict for python3.6 support
            # https://stackoverflow.com/questions/39980323/are-dictionaries-ordered-in-python-3-6
            acls[permission.access_list.name] = OrderedDict(
                {
                    item.name: False
                    for item in sorted(
                        domain.permissions, key=lambda item: item.bitindex
                    )
                }
            )

        for permission in permissions:
            acls[permission.access_list.name][permission.permission.name] = True

        bitmasks = {
            key: int("".join([str(int(item)) for item in value.values()]), 2)
            for key, value in acls.items()
        }

        claims = new.make_public_claims()
        claims.update({"ksk-pem": bitmasks})

        new.claims = claims

        return new
