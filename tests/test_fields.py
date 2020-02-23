import enum
from pathlib import Path

import marshmallow
import pytest

from keyosk import fields


class DemoEnum(enum.Enum):
    DEATH = "star"
    YAVIN = 4
    DARTH = "vader"
    FIGHERS = ["xwing", "ywing", "awing"]
    LUKE_SKYWALKER = "jedi-knight"


def test_enumitem_names():
    class TestSchema(marshmallow.Schema):
        iamenum = fields.EnumItem(DemoEnum)

    good_data = [{"iamenum": "DEATH"}, {"iamenum": "YAVIN"}, {"iamenum": "DARTH"}]

    bad_data = [{"iamenum": "death"}, {"iamenum": None}, {"iamenum": 4}]

    serializer = TestSchema()

    for data in good_data:
        loaded = serializer.load(data)
        assert isinstance(loaded["iamenum"], DemoEnum)
        assert data == serializer.dump(loaded)

    for data in bad_data:
        with pytest.raises(marshmallow.ValidationError):
            serializer.load(data)


def test_enumitem_pretty_names():
    class TestSchema(marshmallow.Schema):
        iamenum = fields.EnumItem(DemoEnum, pretty_names=True)

    good_data = [
        {"iamenum": "death"},
        {"iamenum": "luke-skywalker"},
        {"iamenum": "darth"},
    ]

    bad_data = [
        {"iamenum": None},
        {"iamenum": "DEATH"},
        {"iamenum": "LUKE_SKYWALKER"},
        {"iamenum": 4},
        {"iamenum": "vader"},
    ]

    serializer = TestSchema()

    for data in good_data:
        loaded = serializer.load(data)
        assert isinstance(loaded["iamenum"], DemoEnum)
        assert data == serializer.dump(loaded)

    for data in bad_data:
        with pytest.raises(marshmallow.ValidationError):
            serializer.load(data)


def test_enumitem_values():
    class TestSchema(marshmallow.Schema):
        iamenum = fields.EnumItem(DemoEnum, by_value=True)

    good_data = [
        {"iamenum": "star"},
        {"iamenum": 4},
        {"iamenum": ["xwing", "ywing", "awing"]},
    ]

    bad_data = [
        {"iamenum": None},
        {"iamenum": "DEATH"},
        {"iamenum": "LUKE_SKYWALKER"},
        {"iamenum": "VADER"},
    ]

    serializer = TestSchema()

    for data in good_data:
        loaded = serializer.load(data)
        assert isinstance(loaded["iamenum"], DemoEnum)
        assert data == serializer.dump(loaded)

    for data in bad_data:
        with pytest.raises(marshmallow.ValidationError):
            serializer.load(data)


def test_enumitem_none():
    class TestSchema(marshmallow.Schema):
        iamenum = fields.EnumItem(DemoEnum, allow_none=True)

    good_data = [{"iamenum": "DEATH"}, {"iamenum": "LUKE_SKYWALKER"}, {"iamenum": None}]

    serializer = TestSchema()

    for item in good_data:
        loaded = serializer.load(item)
        if item["iamenum"] is None:
            assert loaded["iamenum"] is None
        else:
            assert isinstance(loaded["iamenum"], DemoEnum)
        assert item == serializer.dump(loaded)


def test_pathstring():
    class TestSchema(marshmallow.Schema):
        iampath = fields.PathString()

    good_data = [
        {"iampath": "/etc/sooper/seekret/place.stuff"},
        {"iampath": "fizzbuzz.foobar"},
    ]

    bad_data = [
        {"iampath": ["/foo", "bar", "baz.stuff"]},
        {"iampath": None},
    ]

    serializer = TestSchema()

    for data in good_data:
        loaded = serializer.load(data)
        assert isinstance(loaded["iampath"], Path)
        assert data == serializer.dump(loaded)

    for data in bad_data:
        with pytest.raises(marshmallow.ValidationError):
            serializer.load(data)
