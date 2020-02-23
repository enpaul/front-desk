import marshmallow as msh


class AccountACLSerializer(msh.Schema):

    access_list = msh.fields.String(required=True, data_key="access-list")
    permission = msh.fields.String(required=True)
    with_server_secret = msh.fields.Boolean(
        required=True, data_key="with-server-secret"
    )
    with_client_secret = msh.fields.Boolean(
        required=True, data_key="with-client-secret"
    )
