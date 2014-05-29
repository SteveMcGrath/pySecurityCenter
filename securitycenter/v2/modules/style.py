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

    def delete_simulate(self, *ids):
        return self._request('deleteSimulate', {
            'styles': [{'id': id} for id in ids]
        })['effects']

    def delete(self, *ids):
        """Deletes a specific style.

        :param *ids: the id of specified style

        :return: dict containing the id of the deleted style
        """

        return self._request('delete', {
            'styles': [{'id': id} for id in ids]
        })['styles']

    def add_family(self):
        #TODO style::addFamily
        raise NotImplementedError

    def delete_family(self):
        #TODO style::deleteFamily
        raise NotImplementedError