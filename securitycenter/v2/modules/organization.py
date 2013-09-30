from .base import Module, extract_value


class Organization(Module):
    _name = 'organization'

    @extract_value('organizations')
    def init(self):
        return self._request('init')

    def add(self):
        #TODO organization:add
        raise NotImplementedError

    def edit(self):
        #TODO organization:edit
        raise NotImplementedError

    def delete(self, *ids):
        """Deletes a specific organization.

        :param *ids: the id of specified organization

        :return: dict containing the id of the deleted organization
        """

        return self._request('delete', {
            'organizations': [{'id': o_id} for o_id in ids]
        })['organizations']

    def validate_add(self):
        #TODO organization:validateAdd
        raise NotImplementedError

    def validate_edit(self):
        #TODO organization:validateEdit
        raise NotImplementedError