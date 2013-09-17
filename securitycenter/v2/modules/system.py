from calendar import timegm
from datetime import datetime
from .base import Module, extract_value


class System(Module):
    _name = 'system'

    def init(self):
        """Retrieves general system information.

        When using two-way SSL, if the client cert is stored, this call
        will automatically log in the associated user.
        """

        # since this requires the user to be unauthenticated,
        # temporarily store and remove the auth token
        token = self._sc._token

        try:
            self._sc._token = None

            r = self._request('init')
        finally:
            # make sure to restore the auth token
            self._sc._token = token

        token = r.get('token')

        if token:
            # new token, log out of the old session and set
            if self._sc._token:
                self._sc.auth.logout()

            self._sc._token = token

        return r


class Heartbeat(Module):
    _name = 'heartbeat'

    def init(self):
        return self._request('init')

    def beat(self, module=None, module_params=None, messages_viewed=None,
             messages_deleted=None, id=None):
        if messages_viewed is None:
            messages_viewed = []

        if messages_deleted is None:
            messages_deleted = []

        return self._request('beat', {
            'messagesViewed': [{'id': int(m_id)} for m_id in messages_viewed],
            'messagesDeleted': [{'id': int(m_id)}
                                for m_id in messages_deleted],
            'module': module,
            'moduleParams': module_params,
            'id': id
        })


class Message(Module):
    _name = 'message'

    def read_all(self, older_than=None):
        if older_than is None:
            older_than = datetime.utcnow()

        if isinstance(older_than, datetime):
            older_than = timegm(older_than.utctimetuple())

        return self._request('readAll', {'olderThan': older_than})

    def delete_all(self, older_than=None):
        if older_than is None:
            older_than = datetime.utcnow()

        if isinstance(older_than, datetime):
            older_than = timegm(older_than.utctimetuple())

        return self._request('deleteAll', {'olderThan': older_than})

    @extract_value('messages')
    def get_page(self, id=None, size=None):
        return self._request('getPage', {
            'id': id,
            'size': size
        })
