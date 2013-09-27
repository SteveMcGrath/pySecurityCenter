from .base import Module, extract_value


class User(Module):
    _name = 'user'

    @extract_value('users')
    def init(self):
        return self._request('init')

    def add(self):
        #TODO user: add
        raise NotImplementedError

    def edit(self):
        #TODO user:edit
        raise NotImplementedError

    def delete(self):
        #TODO user:delete
        raise NotImplementedError

    def query(self):
        #TODO user:query
        raise NotImplementedError

    def change_password(self):
        #TODO user:changePassword
        raise NotImplementedError

    def get_coverage(self):
        #TODO user:getCoverage
        raise NotImplementedError

    def validate_add(self):
        #TODO user::validateAdd
        raise NotImplementedError

    def validate_edit(self):
        #TODO user::validateEdit
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