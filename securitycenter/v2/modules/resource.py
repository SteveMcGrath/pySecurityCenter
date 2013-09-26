from .base import Module, extract_value


class Resource(Module):
    _name = 'resource'

    @extract_value('scanners')
    def init(self):
        return self._request('init')