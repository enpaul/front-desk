import datetime
import enum
import time
from pathlib import Path

import marshmallow
import pytest

from keyosk import _fields as fields


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


def test_pathstring_none():
    class TestSchema(marshmallow.Schema):
        iampath = fields.PathString(allow_none=True)

    good_data = [
        {"iampath": "/etc/sooper/seekret/place.stuff"},
        {"iampath": "fizzbuzz.foobar"},
        {"iampath": None},
    ]

    serializer = TestSchema()

    for item in good_data:
        loaded = serializer.load(item)
        if item["iampath"] is None:
            assert loaded["iampath"] is None
        else:
            assert isinstance(loaded["iampath"], Path)
        assert item == serializer.dump(loaded)


def test_epoch():
    class TestSchema(marshmallow.Schema):
        iamepoch = fields.Epoch()

    good_data = [
        {"iamepoch": 123456789},
        {"iamepoch": 0},
        {"iamepoch": int(time.time())},
    ]

    bad_data = [
        {"iamepoch": -1},
        {"iamepoch": (1, 2, 3)},
        {"iamepoch": datetime.datetime.utcnow()},
        {"iamepoch": -1234},
        {"iamepoch": None},
    ]

    serializer = TestSchema()

    for data in good_data:
        loaded = serializer.load(data)
        assert isinstance(loaded["iamepoch"], datetime.datetime)
        assert int(loaded["iamepoch"].timestamp()) == data["iamepoch"]
        assert data == serializer.dump(loaded)

    for data in bad_data:
        with pytest.raises(marshmallow.ValidationError):
            serializer.load(data)


def test_epoch_none():
    class TestSchema(marshmallow.Schema):
        iamepoch = fields.Epoch(allow_none=True)

    good_data = [
        {"iamepoch": 123456789},
        {"iamepoch": 0},
        {"iamepoch": int(time.time())},
        {"iamepoch": None},
    ]

    serializer = TestSchema()

    for item in good_data:
        loaded = serializer.load(item)
        if item["iamepoch"] is None:
            assert loaded["iamepoch"] is None
        else:
            assert isinstance(loaded["iamepoch"], datetime.datetime)
            assert int(loaded["iamepoch"].timestamp()) == item["iamepoch"]
        assert item == serializer.dump(loaded)


def test_rawmultitype():
    class TestSchema(marshmallow.Schema):
        iamraw = fields.RawMultiType([str, bool, datetime.datetime, Path])

    good_data = [
        {"iamraw": "haveyoueverheardthetragedyofdarthplageiusthewise"},
        {"iamraw": True},
        {"iamraw": datetime.datetime.utcnow()},
        {"iamraw": Path("/all", "your", "hackz", "are", "belong", "to", "me")},
    ]

    bad_data = [
        {"iamraw": 1234},
        {"iamraw": datetime.timedelta(seconds=30)},
        {"iamraw": ["hello", "there"]},
        {"iamraw": None},
    ]

    serializer = TestSchema()

    for data in good_data:
        loaded = serializer.load(data)
        assert loaded == data
        assert data == serializer.dump(loaded)

    for data in bad_data:
        with pytest.raises(marshmallow.ValidationError):
            serializer.load(data)


def test_rawmultitype_none():
    class TestSchema(marshmallow.Schema):
        iamraw = fields.RawMultiType([str, datetime.datetime], allow_none=True)

    good_data = [
        {"iamraw": "haveyoueverheardthetragedyofdarthplageiusthewise"},
        {"iamraw": datetime.datetime.utcnow()},
        {"iamraw": None},
    ]

    serializer = TestSchema()

    for data in good_data:
        loaded = serializer.load(data)
        assert loaded == data
        assert data == serializer.dump(loaded)
