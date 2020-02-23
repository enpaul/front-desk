from typing import List
from typing import Type

from keyosk.resources._shared import KeyoskResource
from keyosk.resources.account import AccountMultiResource
from keyosk.resources.account import AccountPermissionResource
from keyosk.resources.account import AccountSingleResource
from keyosk.resources.auth import AuthenticationResource
from keyosk.resources.blacklist import BlacklistResource
from keyosk.resources.domain import DomainAuditResource
from keyosk.resources.domain import DomainMultiResource
from keyosk.resources.domain import DomainSingleResource
from keyosk.resources.openapi import OpenAPIResource
from keyosk.resources.public_key import PublicKeyResource


RESOURCES: List[Type[KeyoskResource]] = [
    AuthenticationResource,
    OpenAPIResource,
    PublicKeyResource,
    BlacklistResource,
    DomainMultiResource,
    DomainSingleResource,
    DomainAuditResource,
    AccountMultiResource,
    AccountSingleResource,
    AccountPermissionResource,
]
