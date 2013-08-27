from .base import Module, extract_value


class User(Module):
    _name = "user"

    @extract_value("users")
    def init(self):
        return self._request("init")

    #TODO user
