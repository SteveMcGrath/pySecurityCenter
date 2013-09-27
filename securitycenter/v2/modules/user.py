from .base import Module, extract_value


class User(Module):
    _name = 'user'

    @extract_value('users')
    def init(self):
        return self._request('init')

    #TODO user


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