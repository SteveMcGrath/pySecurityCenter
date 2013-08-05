from calendar import timegm
from datetime import datetime


class Module(object):
    _name = ""

    def __init__(self, sc):
        self._sc = sc

    def _request(self, action, input=None, parse=True):
        return self._sc._request(self._name, action, input, parse)


class System(Module):
    _name = "system"

    def init(self):
        token = self._sc._token

        try:
            self._sc._token = None

            r = self._request("init")
        finally:
            self._sc._token = token

        token = r.get("token")

        if token:
            if self._sc._token:
                self._sc.auth.logout()

            self._sc._token = token

        return r


class Auth(Module):
    _name = "auth"

    def login(self, username, password):
        if self._sc._token:
            self.logout()

        r = self._request("login", {
            "username": username,
            "password": password
        })

        self._sc._token = r["token"]

        return r

    def logout(self):
        r = self._request("logout")

        self._sc._token = None
        self._sc._session.cookies.clear()

        return r

    def save_fingerprint(self):
        return self._request("saveFingerprint")


class Plugin(Module):
    _name = "plugin"

    def _fetch(self, action, size, offset, type, sort_field, sort_direction, filter_field, filter_string, since):
        if isinstance(since, datetime):
            since = timegm(since.utctimetuple())

        return self._request(action, {
            "size": size,
            "offset": offset,
            "type": type,
            "sortField": sort_field,
            "sortDirection": sort_direction,
            "filterField": filter_field,
            "filterString": filter_string,
            "since": since
        })

    def init(self, size=None, offset=None, type=None, sort_field=None, sort_direction=None, filter_field=None, filter_string=None, since=None):
        return self._fetch("init", size, offset, since, type, sort_field, sort_direction, filter_field, filter_string)

    def get_page(self, size=None, offset=None, since=None, type=None, sort_field=None, sort_direction=None, filter_field=None, filter_string=None):
        return self._fetch("getPage", size, offset, since, type, sort_field, sort_direction, filter_field, filter_string)

    def get_details(self, plugin_id):
        return self._request("getDetails", {"pluginID": plugin_id})

    def get_source(self, plugin_id):
        return self._request("getSource", {"pluginID": plugin_id})

    def get_families(self):
        return self._request("getFamilies")

    def get_plugins(self, family_ids):
        return self._request("getPlugins", {
            "families": [{"id": int(id)} for id in family_ids]
        })

    def update(self, type="all"):
        return self._request("update", {"type": type})

    def upload(self):
        raise NotImplementedError


class Credential(Module):
    _name = "credential"

    def init(self):
        return self._request("init")

    def add(self):
        raise NotImplementedError

    def edit(self):
        raise NotImplementedError

    def share_simulate(self):
        raise NotImplementedError

    def share(self):
        raise NotImplementedError

    def delete_simulate(self):
        raise NotImplementedError

    def delete(self):
        raise NotImplementedError


class Heartbeat(Module):
    _name = "heartbeat"

    def init(self):
        return self._request("init")

    def beat(self, module=None, module_params=None, messages_viewed=None, messages_deleted=None, id=None):
        if messages_viewed is None:
            messages_viewed = []

        if messages_deleted is None:
            messages_deleted = []

        return self._request("beat", {
            "messagesViewed": [{"id": int(m_id)} for m_id in messages_viewed],
            "messagesDeleted": [{"id": int(m_id)} for m_id in messages_deleted],
            "module": module,
            "moduleParams": module_params,
            "id": id
        })


class Message(Module):
    _name = "message"

    def read_all(self, older_than=None):
        if older_than is None:
            older_than = datetime.utcnow()

        if isinstance(older_than, datetime):
            older_than = timegm(older_than.utctimetuple())

        return self._request("readAll", {"olderThan": older_than})

    def delete_all(self, older_than=None):
        if older_than is None:
            older_than = datetime.utcnow()

        if isinstance(older_than, datetime):
            older_than = timegm(older_than.utctimetuple())

        return self._request("deleteAll", {"olderThan": older_than})
