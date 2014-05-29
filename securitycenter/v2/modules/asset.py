from .base import Module, extract_value


class Asset(Module):
    _name = 'asset'

    @extract_value('assets')
    def init(self):
        return self._request('init')

    @extract_value('viewable_ips')
    def get_ips(self, id, ips_only=False):
        return self._request('getIPs', {
            'id': id,
            'ipsOnly': int(ips_only)
        })

    def combine(self, ids, ips, operator):
        # operator is union, intersection, difference, or complement
        return self._request('combine', {
            'assetIDs': [{'id': id} for id in ids],
            'definedIPs': ips,
            'operator': operator
        })

    def add(self):
        #TODO asset::add
        raise NotImplementedError

    def edit(self):
        #TODO asset::edit
        raise NotImplementedError

    def share_simulate(self, id, users):
        return self._request('shareSimulate', {
            'id': id,
            'users': [{'id': u_id} for u_id in users]
        })['effects']

    def share(self, id, users):
        return self._request('share', {
            'id': id,
            'users': [{'id': u_id} for u_id in users]
        })

    def delete_simulate(self, *ids):
        return self._request('deleteSimulate', {
            'assets': [{'id': id} for id in ids]
        })['effects']

    def delete(self, *ids):
        return self._request('delete', {
            'assets': [{'id': id} for id in ids]
        })['assets']
