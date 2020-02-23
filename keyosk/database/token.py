import datetime
import json
from collections import OrderedDict
from typing import Sequence

import peewee

from keyosk import datatypes
from keyosk.database._shared import KeyoskBaseModel
from keyosk.database.account import Account
from keyosk.database.account_acl import AccountACLEntry
from keyosk.database.domain import Domain


class Token(KeyoskBaseModel):
    class Meta:
        table_name = "token"

    account = peewee.ForeignKeyField(Account, backref="tokens")
    domain = peewee.ForeignKeyField(Domain, backref="tokens")
    issuer = peewee.CharField(null=False)
    issued = peewee.DateTimeField(null=False, default=datetime.datetime.utcnow)
    expires = peewee.DateTimeField(null=False)
    revoked = peewee.BooleanField(null=False)
    _claims = peewee.CharField(null=False)
    _usage = peewee.CharField(null=False)

    @property
    def claims(self):
        return json.loads(self._claims)

    @claims.setter
    def claims(self, value):
        self._claims = json.dumps(value)

    @property
    def usage(self) -> datatypes.TokenUsage:
        return datatypes.TokenUsage[self._usage]

    @usage.setter
    def usage(self, value: datatypes.TokenUsage):
        self._usage = value.name

    def make_public_claims(self):
        return {
            "jti": self.uuid,
            "sub": self.account.username,
            "aud": self.domain.audience,
            "iss": self.issuer,
            "exp": int(self.expires.timestamp()),
            "iat": int(self.issued.timestamp()),
        }

    @classmethod
    def factory(
        cls,
        account: Account,
        domain: Domain,
        issuer: str,
        lifespan: datetime.timedelta,
        usage: datatypes.TokenUsage,
        permissions: Sequence[AccountACLEntry],
    ):
        new = cls(
            account=account,
            domain=domain,
            issuer=issuer,
            expires=(datetime.datetime.utcnow() + lifespan),
            usage=usage,
            revoked=False,
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
        claims.update({"ksk-usg": new.usage.value, "ksk-pem": bitmasks})

        new.claims = claims

        return new
