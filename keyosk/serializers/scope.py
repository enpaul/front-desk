from typing import Any
from typing import Dict

import marshmallow as msh
from playhouse import shortcuts

from keyosk.database import KeyoskAccountScope


class AccountScopeSerializer(msh.Schema):

    access_list = msh.fields.String(required=True, data_key="access-list")
    permission = msh.fields.String(required=True)
    with_server_secret = msh.fields.Boolean(
        required=True, data_key="with-server-secret"
    )
    with_client_secret = msh.fields.Boolean(
        required=True, data_key="with-client-secret"
    )

    @staticmethod
    @msh.post_load
    def _make_model(data: Dict[str, Any], **kwargs) -> KeyoskAccountScope:
        return KeyoskAccountScope(**data)

    @staticmethod
    @msh.pre_dump
    def _unmake_model(data: KeyoskAccountScope, **kwargs) -> Dict[str, Any]:
        return shortcuts.model_to_dict(data, recurse=False, backrefs=False,)
