from .base import Module, extract_value


class Repository(Module):
    _name = "repository"

    @extract_value("repositories")
    def init(self):
        return self._request("init")

    #TODO repository
