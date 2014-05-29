from .base import Module


class Resource(Module):
    _name = 'resource'

    def init(self):
        return self._request('init')