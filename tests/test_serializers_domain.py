# pylint: disable=unused-argument,redefined-outer-name,unused-import
import pytest
from fixtures import demo_database

from keyosk import database
from keyosk import serializers


def test_roundtrip(demo_database):
    serializer = serializers.DomainSerializer()

    for domain in database.KeyoskDomain.select():
        dumped = serializer.dump(domain)
        assert sorted(dumped["permissions"]) == sorted(
            [permission.name for permission in domain.permissions]
        )
        assert sorted(dumped["access-lists"]) == sorted(
            acl.name for acl in domain.access_lists
        )
        assert domain == serializer.load(dumped)
