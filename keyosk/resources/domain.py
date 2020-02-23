from keyosk.resources._shared import KeyoskResource
from keyosk.resources._shared import ResponseTuple


class DomainMultiResource(KeyoskResource):

    ROUTES = ("/domain/",)

    def get(self) -> ResponseTuple:
        raise NotImplementedError

    def post(self) -> ResponseTuple:
        raise NotImplementedError

    def head(self) -> ResponseTuple:
        return self._head(self.get())


class DomainSingleResource(KeyoskResource):

    ROUTES = "/domain/<string:domain_ref>/"

    def get(self, domain_ref: str) -> ResponseTuple:
        raise NotADirectoryError

    def patch(self, domain_ref: str) -> ResponseTuple:
        raise NotADirectoryError

    def delete(self, domain_ref: str) -> ResponseTuple:
        raise NotADirectoryError

    def head(self, domain_ref: str) -> ResponseTuple:
        return self._head(self.get(domain_ref))


class DomainAuditResource(KeyoskResource):

    ROUTES = "/domain/<string:domain_ref>/audit"

    def get(self, domain_ref: str) -> ResponseTuple:
        raise NotADirectoryError

    def head(self, domain_ref: str) -> ResponseTuple:
        return self._head(self.get(domain_ref))
