from .base import Module, extract_value


class Alert(Module):
    _name = "alert"

    @extract_value('alerts')
    def init(self):
        """Returns a list of all alerts and their metadata.

        """
        return self._request('init')

    def edit(self):
        #TODO alert::edit
        raise NotImplementedError

    def delete(self, owner, *ids):
        """Deletes alerts.

        :param owner: owner's ID
        :param ids: alert IDs

        :return params
        """
        return self._request('delete', {
            'alerts': [{'id': id} for id in ids],
            'ownerID': owner
        })['alerts']

    def execute(self, id):
        return self._request('execute', {
            'id': id
        })

    def query(self, start=None, stop=None, sort=None, direction=None,
              filters=None, tool=None):
        """Queries Alert module

        :param start: startOffset
        :param stop: endOffset
        :param sort: sortField
        :param direction: sortDir
        :param filters: filters
        :param tool: tool

        :return params
        """

        input = {
            'startOffset': start, 'endOffset': stop,
            'sortField': sort, 'sortDir': direction and direction.upper(),
            'filters': filters, 'tool': tool
        }

        return self._request('query', input)

    def validate_add(self):
        #TODO alert::validateAdd
        raise NotImplementedError

    def validate_edit(self):
        #TODO alert::validateEdit
        raise NotImplementedError
