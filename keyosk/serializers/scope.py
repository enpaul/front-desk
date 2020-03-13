from typing import Any
from typing import Dict
from typing import Union

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

    @msh.post_load
    def _make_model(self, data: Dict[str, Any], **kwargs) -> KeyoskAccountScope:
        return KeyoskAccountScope(**data)

    @msh.pre_dump
    def _unmake_model(
        self, data: Union[Dict[str, Any], KeyoskAccountScope], **kwargs
    ) -> Dict[str, Any]:
        if isinstance(data, KeyoskAccountScope):
            return shortcuts.model_to_dict(data, recurse=False, backrefs=False)
        return data
