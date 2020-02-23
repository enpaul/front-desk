from keyosk.resources._shared import KeyoskResource
from keyosk.resources._shared import ResponseTuple


class AuthenticationResource(KeyoskResource):

    ROUTES = "/auth/<string:domain_ref>"

    def get(self, domain_ref: str) -> ResponseTuple:
        raise NotADirectoryError

    def head(self, domain_ref: str) -> ResponseTuple:
        raise NotImplementedError
