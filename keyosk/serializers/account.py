import datetime
from typing import Any
from typing import Dict
from typing import Union
from uuid import UUID
from uuid import uuid4

import marshmallow as msh
from playhouse import shortcuts

from keyosk._fields import Epoch
from keyosk._fields import RawMultiType
from keyosk.database import KeyoskAccount
from keyosk.serializers.scope import AccountScopeSerializer


class AccountSerializer(msh.Schema):

    uuid = msh.fields.UUID(required=True)
    created = Epoch(required=True)
    updated = Epoch(required=True)
    username = msh.fields.String(required=True)
    enabled = msh.fields.Boolean(required=True)
    extras = msh.fields.Dict(
        keys=msh.fields.String(),
        values=RawMultiType([int, float, bool, str], allow_none=True),
        required=True,
    )
    scopes = msh.fields.List(msh.fields.Nested(AccountScopeSerializer), required=True)

    @staticmethod
    @msh.post_load
    def _make_model(data: Dict[str, Any], **kwargs) -> KeyoskAccount:
        scopes = []
        for item in data["scopes"]:
            item.account_id = data["uuid"]
            scopes.append(item)
        data["scopes"] = scopes
        return KeyoskAccount(**data)

    @staticmethod
    @msh.pre_dump
    def _unmake_model(data: KeyoskAccount, **kwargs) -> Dict[str, Any]:
        return shortcuts.model_to_dict(
            data, recurse=False, backrefs=True, extra_attrs=["extras"],
        )

    @classmethod
    def update(cls, uuid: Union[str, uuid.UUID], data: Dict[str, Any]) -> KeyoskAccount:
        data.update({"uuid": UUID(str(uuid))})
        loaded = cls(exclude=["created", "updated"]).load(data)
        loaded.updated = datetime.datetime.utcnow()
        return loaded

    @classmethod
    def create(cls, data: Dict[str, Any]) -> KeyoskAccount:
        data.update({"uuid": uuid4()})
        loaded = cls(exclude=["created", "updated"]).load(data)
        loaded.updated = datetime.datetime.utcnow()
        loaded.created = datetime.datetime.utcnow()
        return loaded
