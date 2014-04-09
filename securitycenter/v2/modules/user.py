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

    def add(self, username, role_id, first_name, last_name=None, title=None, phone=None, email=None):
        """Add user.

        :param first_name: user first name
        :param last_name: user last name
        :param title: user title
        :param role_id: user role
        :param phone: user phone number
        :param email: user email
        :param username: user username

        :return: returns response
        """
        #TODO: add support for lces, id, fingerprint, repositories, state, city
        #TODO: add support for queries, assets, address, authType, policies
        #TODO: add support for country, credentials
        return self._request('add', {
            'lces': [],
            'firstname': first_name,
            'id': "no_id",
            'lastname': last_name,
            'address': "",
            'authType': "ldap",
            'fingerprint': "",
            'roleID': role_id,
            'title': title,
            'repositories': [],
            'state': "",
            'city': "",
            'policies': [],
            'country': "",
            'phone': phone,
            'parentID': "1",
            'credentials': [],
            'queries': [],
            'email': email,
            'assets': {'isAccessible': [],
                       'definesUser': [{'id': "0"}]},
            'username': username
        })

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

        :return: return params used
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


class UserPrefs(Module):
    _name = 'userPrefs'

    def init(self):
        return self._request('init')

    def set(self, id, timezone):
        """Set user preferences. Attributes are optional for normal users.

        :param id: the user id
        :param timezone: preferred timezone

        :return: return params used
        """

        return self._request('set', {
            'userID': id,
            'prefTimeZone': timezone
        })

    def set_module_prefs(self):
        #TODO user:setModulePrefs
        raise NotImplementedError
