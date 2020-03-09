import datetime
import re
from typing import Any
from typing import Dict
from typing import List
from typing import Union
from uuid import UUID
from uuid import uuid4

import marshmallow as msh
from playhouse import shortcuts

from keyosk import constants
from keyosk._fields import Epoch
from keyosk.database import KeyoskDomain
from keyosk.database import KeyoskDomainAccessList
from keyosk.database import KeyoskDomainPermission


class DomainSerializer(msh.Schema):
    """Serializer for domain records

    This serializer is meant to translate between the client-facing data format and a
    data format that is ready to be used with the :class:`database.Domain` model for
    access to and from the database.

    .. note:: Schema fields here map 1:1 with the model fields/properties of the same
              names on :class:`database.Domain`.
    """

    uuid = msh.fields.UUID(required=True)
    created = Epoch(required=True)
    updated = Epoch(required=True)
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
    access_lists = msh.fields.Method(
        serialize="serialize_access_lists",
        deserialize="deserialize_access_lists",
        required=True,
        data_key="access-lists",
    )
    permissions = msh.fields.Method(
        serialize="serialize_permissions",
        deserialize="deserialize_permissions",
        required=True,
    )

    @staticmethod
    def deserialize_access_lists(value: List[str]) -> List[KeyoskDomainAccessList]:
        models = []
        errors = {}
        for index, item in enumerate(set(value)):
            if not isinstance(item, str):
                errors[index] = f"Invalid type '{type(item)}', expected 'str'"
            elif not re.search(constants.REGEX_DOMAIN_ACCESS_LIST_NAME, item):
                errors[
                    index
                ] = f"Invalid format for value '{item}', must match '{constants.REGEX_DOMAIN_ACCESS_LIST_NAME}'"
            else:
                models.append(KeyoskDomainAccessList(name=item))

        if errors:
            raise msh.ValidationError(errors)

        return models

    @staticmethod
    def serialize_access_lists(obj: Dict[Any, Any]) -> List[str]:
        return [item.name for item in obj["access_lists"]]

    @staticmethod
    def deserialize_permissions(value: List[str]) -> List[KeyoskDomainPermission]:
        models = []
        errors = {}
        for index, item in enumerate(set(value)):
            if not isinstance(item, str):
                errors[index] = f"Invalid type '{type(item)}', expected 'str'"
            elif not re.search(constants.REGEX_DOMAIN_PERMISSION_NAME, item):
                errors[
                    index
                ] = f"Invalid format for value '{item}', must match '{constants.REGEX_DOMAIN_PERMISSION_NAME}'"
            else:
                models.append(KeyoskDomainPermission(name=item))

        if errors:
            raise msh.ValidationError(errors)

        return models

    @staticmethod
    def serialize_permissions(obj: Dict[Any, Any]) -> List[str]:
        return [item.name for item in obj["permissions"]]

    @staticmethod
    @msh.post_load
    def _make_model(data: Dict[str, Any], **kwargs) -> KeyoskDomain:
        acls = []
        for item in data["access_lists"]:
            item.domain_id = data["uuid"]
            acls.append(item)
        data["access_lists"] = acls

        permissions = []
        for item in data["permissions"]:
            item.domain_id = data["uuid"]
            permissions.append(item)
        data["permissions"] = permissions

        return KeyoskDomain(**data)

    @staticmethod
    @msh.pre_dump
    def _unmake_model(data: KeyoskDomain, **kwargs) -> Dict[str, Any]:
        return shortcuts.model_to_dict(
            data,
            recurse=False,
            backrefs=True,
            extra_attrs=["lifespan_access", "lifespan_refresh",],
        )

    @classmethod
    def update(cls, uuid: Union[str, uuid.UUID], data: Dict[str, Any]) -> KeyoskDomain:
        data.update({"uuid": UUID(str(uuid))})
        loaded = cls(exclude=["created", "updated"]).load(data)
        loaded.updated = datetime.datetime.utcnow()
        return loaded

    @classmethod
    def create(cls, data: Dict[str, Any]) -> KeyoskDomain:
        data.update({"uuid": uuid4()})
        loaded = cls(exclude=["created", "updated"]).load(data)
        loaded.updated = datetime.datetime.utcnow()
        loaded.created = datetime.datetime.utcnow()
        return loaded
