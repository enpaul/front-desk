import marshmallow as msh


class DomainSerializer(msh.Schema):

    uuid = msh.fields.UUID(required=True)
    created = msh.fields.DateTime(required=True)
    updated = msh.fields.DateTime(required=True)
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
    access_list_names = msh.fields.List(
        msh.fields.String(), required=True, data_key="access-lists"
    )
    permission_names = msh.fields.List(
        msh.fields.String(), required=True, data_key="permissions"
    )
