"""Internally shared database components

This submodule exists to avoid circular imports: architecturally there's no reason why
this module's base model and the :func:`initialize` function cannot both go in
``__init__``, or indeed why they can't both go here. However if both existed in the same
module then every other submodule would need to both import :class:`KeyoskBaseModel`
from that module, and be imported into that module for the :func:`initialize` function
to work. This would lead to a circular import.

Thus the :func:`initialize` function and :class:`KeyoskBaseModel` class need to go in
separate modules, and for somewhat arbitrary reasons the base model was put here and the
init function kept in init.
"""
import uuid
from typing import Any
from typing import Generator
from typing import List
from typing import Tuple

import peewee


INTERFACE = peewee.DatabaseProxy()


class KeyoskBaseModel(peewee.Model):
    """Base model for primary models to inherit from

    * Attaches the ``uuid`` field to the model as the primary key
    * Attaches the model- and all child models- to the database proxy
    * Provides the structure for casting the model to a dictionary

    .. warning:: This model is a stub and should not be created in the database or
                 used for querying.
    """

    class Meta:  # pylint: disable=missing-docstring,too-few-public-methods
        database = INTERFACE

    uuid = peewee.UUIDField(
        null=False, unique=True, primary_key=True, default=uuid.uuid4
    )

    @staticmethod
    def dict_keys() -> List[str]:
        """Return tuple of attribute names that should be included in the dict form of the model
        Inteneded to be used in a dictionary comprehension; see the :meth:`__iter__` method for
        usage example.
        """
        return []

    @staticmethod
    def foreign_ref() -> List[str]:
        """Return tuple of attribute names that point to foreign key references on the model
        Intended for usage when recursively converting models into dictionaries ahead of
        serialization; see the :meth:`__iter__` method for usage example.

        .. warning:: Foreign keys should only be included here when their attribute appears in the
                     tuple returned from :meth:`dict_keys`
        """
        return []

    @staticmethod
    def foreign_backref() -> List[str]:
        """Return tuple of attribute names that point to foreign backreferences on the model
        Inteneded for usage when recursively converting models into dictionaries ahead of
        serialization; see the :meth:`__iter__` method for usage example.

        .. warning:: Foreign keys should only be included here when their attribute appears in the
                     tuple returned from :meth:`dict_keys`
        """
        return []

    def __iter__(self) -> Generator[Tuple[str, Any], None, None]:
        for key in self.dict_keys():
            if key in self.foreign_ref():
                yield key, dict(getattr(self, key))
            elif key in self.foreign_backref():
                yield key, [dict(item) for item in getattr(self, key)]
            else:
                yield key, getattr(self, key)
