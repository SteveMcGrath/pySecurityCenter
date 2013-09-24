from .base import Module


class Status(Module):
    _name = 'status'

    def init(self):
        return self._request('init')