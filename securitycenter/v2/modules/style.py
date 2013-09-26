from .base import Module, extract_value


class Style(Module):
    _name = 'style'

    @extract_value('styles')
    def init(self):
        return self._request('init')

    def add(self):
        #TODO style::add
        raise NotImplementedError

    def edit(self):
        #TODO style::edit
        raise NotImplementedError

    def delete(self):
        #TODO style::delete
        raise NotImplementedError

    def add_family(self):
        #TODO style::addFamily
        raise NotImplementedError

    def delete_family(self):
        #TODO style::deleteFamily
        raise NotImplementedError