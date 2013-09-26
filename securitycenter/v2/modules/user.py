from .base import Module, extract_value


class User(Module):
    _name = 'user'

    @extract_value('users')
    def init(self):
        return self._request('init')

    def delete(self, *ids):
        """Deletes user

        :param ids: list of user ids

        "return: returns response
        """
        return self._request('delete', {
            'users': [{'id': id} for id in ids]
        })

    def add(self):
        #TODO: user::add
        raise NotImplementedError

    def edit(self):
        #TODO user::edit
        raise NotImplementedError

    def query(self, ids, start=None, sort=None, stop=None,
              tool=None, password=None):
        """Query Users module.

        :param ids: specified user filters IDs
        :param start: startOffset
        :param sort: sortField
        :param stop: endOffset
        :param tool: query tool
        :param password: user password

        return: return params used
        """

        return self._request('query', {
            'endOffset': stop,
            'startOffset': start,
            'sortField': sort,
            'tool': tool,
            'password': password,
            'filters': [{'id': id} for id in ids]
        })

    def change_password(self,password):
        """Change user's password

        :param password: user's specified password

        :return: returns response
        """

        return self._request('password', {
            'password': password
        })

    def get_coverage(self, user):
        """Get coverage for user.

        :param user: user's ID

        :return: returns user's coverage
        """

        return self._request('getCoverage', {
            'userID': user
        })['userID']

    def validate_add(self):
        #TODO vuln::validateAdd
        raise NotImplementedError

    def validate_edit(self):
        #TODO vuln::validateEdit
        raise NotImplementedError


class Admin(User):
    _name = 'admin'

    #TODO? admin, might be duplicate of user
