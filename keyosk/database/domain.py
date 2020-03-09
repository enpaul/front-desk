"""Authentication domain model definition"""
import datetime

import peewee

from keyosk.database._shared import KeyoskBaseModel


class KeyoskDomain(KeyoskBaseModel):
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
    _lifespan_access = peewee.IntegerField(null=False)
    _lifespan_refresh = peewee.IntegerField(null=False)

    @property
    def lifespan_access(self) -> datetime.timedelta:
        """Return the access lifespan as a timedelta"""
        return datetime.timedelta(seconds=self._lifespan_access)

    @lifespan_access.setter
    def lifespan_access(self, value: datetime.timedelta):
        """Set the access lifespan as an integer from a timedelta"""
        self._lifespan_access = int(value.total_seconds())

    @property
    def lifespan_refresh(self) -> datetime.timedelta:
        """Return the refresh lifespan as a timedelta"""
        return datetime.timedelta(seconds=self._lifespan_refresh)

    @lifespan_refresh.setter
    def lifespan_refresh(self, value: datetime.timedelta):
        """Set the refresh lifespan as an integer from a timedelta"""
        self._lifespan_refresh = int(value.total_seconds())

    def __str__(self) -> str:
        return f"Domain '{self.name}' ({self.uuid})"
