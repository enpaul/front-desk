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
    access_lists = msh.fields.List()

    # created = peewee.DateTimeField(null=False, default=datetime.datetime.utcnow)
    # updated = peewee.DateTimeField(null=False, default=datetime.datetime.utcnow)
    # name = peewee.CharField(null=False, unique=True)
    # audience = peewee.CharField(null=False, unique=True)
    # title = peewee.CharField(null=True)
    # description = peewee.CharField(null=True)
    # contact = peewee.CharField(null=True)
    # enabled = peewee.BooleanField(null=False)
    # enable_client_set_auth = peewee.BooleanField(null=False)
    # enable_server_set_auth = peewee.BooleanField(null=False)
    # enable_refresh = peewee.BooleanField(null=False)
    # lifespan_access = peewee.IntegerField(null=False)
    # lifespan_refresh = peewee.IntegerField(null=False)
