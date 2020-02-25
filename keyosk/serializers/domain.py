from typing import List

import marshmallow as msh

from keyosk import fields as custom_fields
from keyosk.serializers.domain_extras import DomainAccessListSerializer
from keyosk.serializers.domain_extras import DomainPermissionSerializer


class DomainSerializer(msh.Schema):

    uuid = msh.fields.UUID(required=True)
    created = custom_fields.Epoch(required=True)
    updated = custom_fields.Epoch(required=True)
    name = msh.fields.String(required=True)
    audience = msh.fields.String(required=True)
    title = msh.fields.String(required=True, allow_none=True)
    description = msh.fields.String(required=True, allow_none=True)
    contact = msh.fields.String(required=True, allow_none=True)
    enabled = msh.fields.Boolean(required=True)
    enable_client_set_auth = msh.fields.Boolean(
        required=True, data_key="enable-client-set-auth"
    )
    enable_server_set_auth = msh.fields.Boolean(
        required=True, data_key="enable-server-set-auth"
    )
    enable_refresh = msh.fields.Boolean(required=True, data_key="enable-refresh")
    lifespan_access = msh.fields.Boolean(required=True, data_key="lifespan-access")
    lifespan_refresh = msh.fields.Boolean(required=True, data_key="lifespan-refresh")
    access_lists = msh.fields.List(
        msh.fields.Nested(DomainAccessListSerializer),
        required=True,
        data_key="access-lists",
    )
    permissions = msh.fields.List(
        msh.fields.Nested(DomainPermissionSerializer), required=True
    )

    @staticmethod
    def creation_fields() -> List[str]:
        return ["uuid", "created", "updated"]
