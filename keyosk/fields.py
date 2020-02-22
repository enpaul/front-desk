"""Custom fields for handing de/serializing custom data types"""
from enum import Enum
from pathlib import Path
from typing import Any
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
            raise msh.ValidationError(err)
        except (KeyError, AttributeError) as err:
            raise msh.ValidationError(f"No {self.enum} named {err}")

    @staticmethod
    def _to_pretty_name(value: str) -> str:
        return value.replace("_", "-").lower()

    @staticmethod
    def _from_pretty_name(value: str) -> str:
        return value.replace("-", "_").upper()


class Path(msh.fields.String):
    """Translate between a string and a path object"""

    def _serialize(self, value: Union[str, Path], *args, **kwargs) -> str:
        return super()._serialize(str(value), *args, **kwargs)

    def _deserialize(self, value: str, *args, **kwargs) -> Path:
        return Path(super()._deserialize(value, *args, **kwargs))
