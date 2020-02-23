"""Authentication domain model definition"""
import datetime
from typing import List

import peewee

from keyosk.database._shared import KeyoskBaseModel


class Domain(KeyoskBaseModel):
    """Authentication domain storage model

    :attribute created: Datetime indicating when the domain was first created
    :attribute updated: Datetime indicating when the domain was last modified
    :attribute name: Simple URL-friendly name for the domain
    :attribute audience: Value to populate the ``audience`` claim of issued JWTs with
                         when authenticating against this domain
    :attribute title: Human-friendly display name for the domain
    :attribute description: Human-friendly longer description of the domain's usage or
                            purpose
    :attribute contact: Contact link for the domain
    :attribute enabled: Whether the domain is enabled for authentication
    :attribute enable_client_set_auth: Whether to allow accounts to authenticate using
                                       the client-set authentication secret
    :attribute enable_server_set_auth: Whether to allow accounts to authenticate using
                                       the server-set authentication secret
    :attribute lifespan_access: Number of seconds that an issued JWT access token should
                                be valid for
    :attribute lifespan_refresh: Number of seconds an an issued JWT refresh token should
                                 be valid for
    :property administration: Container of additional settings related to the
                              administration of the domain itself
    :property access_list_names: List of Access Control Lists under the domain that accounts
                                 can have permission entries on
    :property permission_names: List of permissions that can be assigned to an account's ACL
                                entry
    """

    class Meta:  # pylint: disable=too-few-public-methods,missing-docstring
        table_name = "domain"

    created = peewee.DateTimeField(null=False, default=datetime.datetime.utcnow)
    updated = peewee.DateTimeField(null=False, default=datetime.datetime.utcnow)
    name = peewee.CharField(null=False, unique=True)
    audience = peewee.CharField(null=False, unique=True)
    title = peewee.CharField(null=True)
    description = peewee.CharField(null=True)
    contact = peewee.CharField(null=True)
    enabled = peewee.BooleanField(null=False)
    enable_client_set_auth = peewee.BooleanField(null=False)
    enable_server_set_auth = peewee.BooleanField(null=False)
    enable_refresh = peewee.BooleanField(null=False)
    lifespan_access = peewee.IntegerField(null=False)
    lifespan_refresh = peewee.IntegerField(null=False)

    @property
    def access_list_names(self) -> List[str]:
        """Return the list of ACL items from the backref"""
        return [item.name for item in self._access_lists]

    @property
    def permission_names(self) -> List[str]:
        """Return the list of permission names from the backref"""
        return [item.name for item in self._permissions]

    @staticmethod
    def dict_keys() -> List[str]:
        return [
            "uuid",
            "created",
            "updated",
            "name",
            "audience",
            "title",
            "description",
            "contact",
            "enabled",
            "enable_password",
            "enable_autopassword",
            "enable_refresh",
            "lifespan_access",
            "lifespan_refresh",
            "access_list_names",
            "permission_names",
        ]


class DomainAccessList(KeyoskBaseModel):
    """Access list name model definition

    :attribute name: Name of the access control list
    :attribute domain: Authentication domain the ACL applies to
    """

    class Meta:  # pylint: disable=missing-docstring,too-few-public-methods
        table_name = "domain_acl"

    name = peewee.CharField(null=False)
    domain = peewee.ForeignKeyField(Domain, backref="access_lists")


class DomainPermission(KeyoskBaseModel):
    """Permission name model definition

    :attribute name: Name of the permission
    :attribute bitindex: Index in the generated bitmask that indicates this permission;
                         zero-indexed
    :attribute domain: Authentication domain the permission should apply to the ACLs of
    """

    class Meta:  # pylint: disable=missing-docstring,too-few-public-methods
        table_name = "domain_permission"

    name = peewee.CharField(null=False)
    bitindex = peewee.IntegerField(null=False)
    domain = peewee.ForeignKeyField(Domain, backref="permissions")
