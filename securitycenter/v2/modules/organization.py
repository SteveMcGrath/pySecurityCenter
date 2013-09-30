from .base import Module, extract_value


class Organization(Module):
    _name = 'organization'

    @extract_value('organizations')
    def init(self):
        return self._request('init')