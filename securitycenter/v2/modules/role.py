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

    def delete(self, *ids):
        """Deletes role by specifying ID

        :param ids: the id of specified role

        :return: the id of the deleted roles
        """

        return self._request('delete', {
            'roles': [{'id': id} for id in ids]
        })['roles']