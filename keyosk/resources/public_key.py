from keyosk.resources._shared import KeyoskResource
from keyosk.resources._shared import ResponseTuple


class PublicKeyResource(KeyoskResource):

    ROUTES = ("/public-key",)

    def get(self) -> ResponseTuple:
        raise NotImplementedError

    def head(self) -> ResponseTuple:
        return self._head(self.get())
