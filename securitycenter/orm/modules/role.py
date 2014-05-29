from .base import Module, extract_value


class Role(Module):
    _name = 'role'

    @extract_value('role')
    def init(self):
        return self._request('init')

    def add(self):
        #TODO role::add
        raise NotImplementedError

    def edit(self):
        #TODO role::edit
        raise NotImplementedError

    def delete_simulate(self, *ids):
        return self._request('deleteSimulate', {
            'roles': [{'id': id} for id in ids]
        })['effects']

    def delete(self, *ids):
        """Deletes a set of roles. All users set to one of these roles will be
        put into the ROLE_NONE role which has very limited permissions.

        :param ids: the id of the selected role
        """

        return self._request('delete', {
            'roles': [{'id': id} for id in ids]
        })['roles']
