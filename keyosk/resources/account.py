from keyosk.resources._shared import KeyoskResource
from keyosk.resources._shared import ResponseTuple


class AccountMultiResource(KeyoskResource):

    ROUTES = ("/account/",)

    def get(self) -> ResponseTuple:
        raise NotImplementedError

    def post(self) -> ResponseTuple:
        raise NotImplementedError

    def head(self) -> ResponseTuple:
        return self._head(self.get())


class AccountSingleResource(KeyoskResource):

    ROUTES = "/account/<string:account_ref>/"

    def get(self, account_ref: str) -> ResponseTuple:
        raise NotADirectoryError

    def patch(self, account_ref: str) -> ResponseTuple:
        raise NotADirectoryError

    def delete(self, account_ref: str) -> ResponseTuple:
        raise NotADirectoryError

    def head(self, account_ref: str) -> ResponseTuple:
        return self._head(self.get(account_ref))


class AccountPermissionResource(KeyoskResource):

    ROUTES = "/account/<string:account_ref>/permission"

    def get(self, account_ref: str) -> ResponseTuple:
        raise NotADirectoryError

    def patch(self, account_ref: str) -> ResponseTuple:
        raise NotADirectoryError

    def head(self, account_ref: str) -> ResponseTuple:
        return self._head(self.get(account_ref))
