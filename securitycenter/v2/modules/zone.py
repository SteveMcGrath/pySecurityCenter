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

    def delete_simulate(self, zone_id):
        return self._request('deleteSimulate', {
            'zones': [{'id': id} for id in zone_id]
        })['effects']

    def delete(self, zone_id):
        """Deletes a specific Zone or group of Zones.
        
        :param zone_id: the id of specified Zone

        :return: dict containing the id of the deleted Zones
        """

        return self._request('delete', {
            'zones': [{'id': id} for id in zone_id]
        })['zones']
