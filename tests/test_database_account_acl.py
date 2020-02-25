import json

import peewee
from fixtures import demo_database

from keyosk import database


def test_formatting(demo_database):
    for acl in database.AccountACLEntry.select():
        assert dict(acl) == json.loads(json.dumps(dict(acl)))
        assert str(acl.uuid) not in str(acl)
