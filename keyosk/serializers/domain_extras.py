from typing import Dict

import marshmallow as msh


class DomainAccessListSerializer(msh.Schema):

    name = msh.fields.String(required=True)

    @msh.pre_load
    def _from_string(self, data: str, *args, **kwargs) -> Dict[str, str]:
        return {"name": data}

    @msh.post_dump
    def _to_string(self, data, *args, **kwargs) -> str:
        return data["name"]


class DomainPermissionSerializer(msh.Schema):

    name = msh.fields.String(required=True)
    bitindex = msh.fields.Integer(required=True, validate=msh.validate.Range(min=0))
