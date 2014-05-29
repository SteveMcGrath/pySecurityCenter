from .base import Module


class Logging(Module):
    _name = "logging"

    def init(self):
        return self._request('init')

    def query(self):
        #TODO logging:query
        raise NotImplementedError