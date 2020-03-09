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

    def save_recursive(self, force_insert: bool = False):
        pass
