# pylint: disable=unused-argument,redefined-outer-name,unused-import
from fixtures import demo_database

from keyosk import database
from keyosk import serializers


def test_compatibility(demo_database):
    serializer = serializers.AccountSerializer()

    for domain in database.KeyoskAccount.select():
        dumped = serializer.dump(domain)
        assert domain == serializer.load(dumped)
