from typing import List

import marshmallow as msh

from keyosk import fields as custom_fields
from keyosk.serializers.account_acl import AccountACLSerializer


class AccountSerializer(msh.Schema):

    uuid = msh.fields.UUID(required=True)
    created = custom_fields.Epoch(required=True)
    updated = custom_fields.Epoch(required=True)
    username = msh.fields.String(required=True)
    enabled = msh.fields.Boolean(required=True)
    extras = msh.fields.Dict(
        keys=msh.fields.String(),
        values=custom_fields.RawMultiType([int, float, bool, str, None]),
        required=True,
    )
    acls = msh.fields.List(msh.fields.Nested(AccountACLSerializer), required=True)

    @staticmethod
    def creation_fields() -> List[str]:
        return ["uuid", "created", "updated"]
