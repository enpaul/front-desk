from keyosk.resources._shared import KeyoskResource
from keyosk.resources._shared import ResponseTuple


class BlacklistResource(KeyoskResource):

    ROUTES = ("/blacklist/",)

    def get(self) -> ResponseTuple:
        raise NotImplementedError

    def post(self) -> ResponseTuple:
        raise NotImplementedError

    def head(self) -> ResponseTuple:
        return self._head(self.get())
