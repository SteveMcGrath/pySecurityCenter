from .base import Module, extract_value


class Zone(Module):
    _name = 'zone'

    @extract_value('zones')
    def init(self):
        return self._request('init')

    def add(self):
        #TODO zone::add
        raise NotImplementedError

    def edit(self):
        #TODO zone::edit
        raise NotImplementedError

    def delete_simulate(self, *ids):
        return self._request('deleteSimulate', {
            'zones': [{'id': id} for id in ids]
        })['effects']

    def delete(self, *ids):
        """Deletes a specific Zone or group of Zones.

        :param *ids: the id of specified Zone

        :return: dict containing the id of the deleted Zones
        """

        return self._request('delete', {
            'zones': [{'id': id} for id in ids]
        })['zones']
