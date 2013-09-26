from .base import Module


class AttributeSet(Module):
    _name = "attributeSet"

    def init(self):
        return self._request('init')

    def add(self):
        #TODO attribute::add
        raise NotImplementedError

    def edit(self):
        #TODO attribute::edit
        raise NotImplementedError

    def delete_simulate(self, *ids):
        return self._request('deleteSimulate', {
            'attributeSets': [{'id': id} for id in ids]
        })['effects']

    def delete(self, *ids):
        """Deletes a specific attribute set.

        :param *ids: the id of specified attribute set

        :return: dict containing the id of the deleted attribute set
        """

        return self._request('delete', {
            'attributeSets': [{'id': id} for id in ids]
        })['attributeSets']

    def validate_add(self, type, attr, description=None):
        """Validate added attribute set.

        :param type: must be a valid type for the attribute set
        :param attr: the attribute
        :param description: description for the attribute set

        :return: information for the valid attribute set that was added
        """

        return self._request('validateAdd', {
            'type': type,
            'attributes': attr,
            'description': description
        })

    def validate_edit(self, id, type, attr, description=None):
        """Validate edited attribute set.

        :param id: valid id for the attribute set
        :param type: must be a valid type for the attribute set
        :param attr: the attribute
        :param description: description: description for the attribute set

        :return: information for the valid attribute set that was edited
        """

        return self._request('validateEdit', {
            'setID': id,
            'type': type,
            'attributes': attr,
            'description': description
        })