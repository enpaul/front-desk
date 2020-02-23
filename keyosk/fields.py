"""Custom fields for handing de/serializing custom data types"""
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any
from typing import Sequence
from typing import Type
from typing import Union

import marshmallow as msh


class EnumItem(msh.fields.Field):
    """Translate between an enum and its value or name"""

    def __init__(
        self,
        enum: Type[Enum],
        *args,
        by_value: bool = False,
        pretty_names: bool = False,
        **kwargs,
    ):
        """Initialize the enum field
        :param enum: The base enumeration to use for de/serializing to/from. Passing in a name/value
                     that does not appear in this enum during de/serialization will result in a
                     :exc:`ValidationError` being raised.
        :param by_value: Whether to perform de/serialization using the enum name or enum value. By
                         default the field will be de/serialized using the enum name, but passing
                         this as true will perform de/serialization using the enum value.
        :param pretty_names: Whether to interperate the enum names as "pretty" names. This will
                             convert between uppercase+underscore-delimited and
                             lowercase+hyphen-delimited. For example, an enum named ``FOO_BAR_BAZ``
                             would become ``foo-bar-baz``. This option has no effect if
                             ``by_value=True`` is passed.
        """

        super().__init__(*args, **kwargs)
        self._by_value = by_value
        self._pretty_names = pretty_names
        self.enum = enum

    def _serialize(self, value: Enum, attr, obj, **kwargs) -> Any:
        """Serialize an enumeration to either its name or value"""
        if getattr(self, "allow_none", False) is True and value is None:
            return None
        if self._by_value:
            return value.value
        if self._pretty_names:
            return self._to_pretty_name(value.name)
        return value.name

    def _deserialize(self, value: Any, attr, data, **kwargs) -> Enum:
        """Serialize the name or value of an enumeration to its corresponding enum"""
        try:
            if self._by_value:
                return self.enum(value)
            if self._pretty_names:
                if value in self.enum.__members__:
                    raise KeyError(value)  # Just gets us down to the keyerror handler
                return self.enum[self._from_pretty_name(value)]
            return self.enum[value]
        except ValueError as err:
            raise msh.ValidationError(str(err))
        except (KeyError, AttributeError) as err:
            raise msh.ValidationError(f"No {self.enum} named {err}")

    @staticmethod
    def _to_pretty_name(value: str) -> str:
        return value.replace("_", "-").lower()

    @staticmethod
    def _from_pretty_name(value: str) -> str:
        return value.replace("-", "_").upper()


class PathString(msh.fields.String):
    """Translate between a string and a path object"""

    def _serialize(self, value: Union[str, Path], attr, obj, **kwargs) -> str:
        return super()._serialize(str(value), attr, obj, **kwargs)

    def _deserialize(self, value: str, attr, data, **kwargs) -> Path:
        return Path(super()._deserialize(value, attr, data, **kwargs))


class Epoch(msh.fields.Field):
    """Translate between datetime objects and an integer reperesenting epoch time"""

    def _serialize(self, value: Union[datetime, int], attr, obj, **kwargs) -> int:
        """Serialize a datetime object to an integer"""

        if isinstance(value, datetime):
            return int(value.timestamp())
        return value

    def _deserialize(self, value: int, attr, data, **kwargs) -> datetime:
        """Deserialize an integer to a datetime object"""

        try:
            if value < 0:
                raise msh.ValidationError(f"Invalid epoch time '{value}'")
        except TypeError:
            raise msh.ValidationError(
                f"Invalid epoch value '{value}' of type '{type(value)}'"
            )
        return datetime.fromtimestamp(int(value))


class RawMultiType(msh.fields.Raw):
    """Like raw, but limits the types the value can be to a specified list

    .. note:: Like the Marshmallow :class:`Raw` field, no additional validation is done on the value
              beyond checking its type.
    """

    def __init__(self, types: Sequence[type], *args, **kwargs):
        """Initialize the field

        :param types: Sequence of types that the value to de/serialize can be
        """
        super().__init__(*args, **kwargs)
        self._types = tuple(types)

    def _deserialize(self, value: Any, attr, data, **kwargs) -> Any:
        """Deserialize the value, raising a validation error if it is not of an allowed type"""
        if not isinstance(value, self._types):
            raise msh.ValidationError(
                f"Invalid value '{value}' of type {type(value)}: expected one of {self._types}"
            )
        return value
