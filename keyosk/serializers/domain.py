from typing import Dict
from typing import List
from typing import Union

import marshmallow as msh

from keyosk import constants
from keyosk import fields as custom_fields


class DomainPermissionSerializer(msh.Schema):
    """"""

    name = msh.fields.String(
        required=True,
        validate=msh.validate.Regexp(constants.REGEX_DOMAIN_PERMISSION_NAME),
    )
    bitindex = msh.fields.Integer(required=True, validate=msh.validate.Range(min=0))


class DomainSerializer(msh.Schema):
    """Serializer for domain records

    This serializer is meant to translate between the client-facing data format and a
    data format that is ready to be used with the :class:`database.Domain` model for
    access to and from the database.

    .. note:: Schema fields here map 1:1 with the model fields/properties of the same
              names on :class:`database.Domain`.
    """

    uuid = msh.fields.UUID(required=True)
    created = custom_fields.Epoch(required=True)
    updated = custom_fields.Epoch(required=True)
    name = msh.fields.String(
        required=True, validate=msh.validate.Regexp(constants.REGEX_DOMAIN_NAME)
    )
    audience = msh.fields.String(
        required=True, validate=msh.validate.Regexp(constants.REGEX_DOMAIN_AUDIENCE)
    )
    title = msh.fields.String(
        required=True,
        allow_none=True,
        validate=msh.validate.Regexp(constants.REGEX_DOMAIN_TITLE),
    )
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
    lifespan_access = msh.fields.TimeDelta(required=True, data_key="lifespan-access")
    lifespan_refresh = msh.fields.TimeDelta(required=True, data_key="lifespan-refresh")
    access_list_names = msh.fields.List(
        msh.fields.String(
            validate=msh.validate.Regexp(constants.REGEX_DOMAIN_ACCESS_LIST_NAME)
        ),
        required=True,
        data_key="access-lists",
    )
    permissions = msh.fields.List(
        msh.fields.Nested(DomainPermissionSerializer), required=True,
    )

    @msh.validates("access_list_names")
    def validate_acl_names(self, data: List[str], **kwargs):
        if len(data) != len(set(data)):
            raise msh.ValidationError("Duplicate access list names")

    @msh.validates("permissions")
    def validate_permissions(self, data: List[Dict[str, Union[str, int]]], **kwargs):
        names = [item["name"] for item in data]
        if len(names) != len(set(names)):
            raise msh.ValidationError("Duplicat permission names")

        indexes = sorted([item["bitindex"] for item in data])
        for index in len(indexes):
            if indexes[index - 1] != (index - 1):
                raise msh.ValidationError(
                    f"Invalid bitindexes provided: expected zero-index sequential sequence, recieved {indexes}"
                )

    @staticmethod
    def creation_fields() -> List[str]:
        return ["uuid", "created", "updated"]
