from base64 import b64decode
from cStringIO import StringIO
from calendar import timegm
from datetime import datetime
from zipfile import ZipFile


class Module(object):
    _name = ""

    def __init__(self, sc):
        self._sc = sc

    def _request(self, action, input=None, file=None, parse=True):
        return self._sc._request(self._name, action, input, file, parse)


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
        try:
            return self._request("logout")
        finally:
            self._sc._token = None
            self._sc._session.cookies.clear()

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

    def get_details(self, id):
        return self._request("getDetails", {"pluginID": id})

    def get_source(self, id):
        return b64decode(self._request("getSource", {"pluginID": id})["source"])

    def get_families(self):
        return self._request("getFamilies")

    def get_plugins(self, families):
        return self._request("getPlugins", {"families": [{"id": int(f_id)} for f_id in families]})

    def update(self, type="all"):
        return self._request("update", {"type": type})

    def upload(self, data, type="custom"):
        filename = self._sc.file.name_or_upload(data)

        return self._request("upload", {"filename": filename, "type": type})


class Credential(Module):
    _name = "credential"

    def init(self):
        return self._request("init")

    def add(self, name, type, description=None, group=None, visibility="user", users=None, **kwargs):
        if users is not None:
            users = [{"id": u_id} for u_id in users]

        kwargs.update({
            "name": name,
            "type": type,
            "description": description,
            "group": group,
            "visibility": visibility,
            "users": users
        })

        return self._request("add", kwargs)

    def add_ssh(self, name, username, password=None, public_key=None, private_key=None, passphrase=None, escalation_type=None, escalation_username=None, escalation_password=None, description=None, group=None, visibility="user", users=None):
        if public_key is not None and private_key is not None:
            public_key = self._sc.file.name_or_upload(public_key)
            private_key = self._sc.file.name_or_upload(private_key)

        return self.add(
            name, "ssh", description, group, visibility, users,
            username=username, password=password,
            publicKey=public_key,
            privateKey=private_key, passphrase=passphrase,
            privilegeEscalation=escalation_type,
            escalationUsername=escalation_username,
            escalationPassword=escalation_password
        )

    def add_windows(self, name, username, password, domain=None, description=None, group=None, visibility="user", users=None):
        return self.add(name, "windows", description, group, visibility, users, username=username, password=password, domain=domain)

    def add_snmp(self, name, community, description=None, group=None, visibility="user", users=None):
        return self.add(name, "snmp", description, group, visibility, users, communityString=community)

    def add_kerberos(self, name, ip, port, protocol, realm, description=None, group=None, visibility="user", users=None):
        return self.add(name, "kerberos", description, group, visibility, users, ip=ip, port=port, protocol=protocol, realm=realm)

    def edit(self, id, prefill=True, name=None, type=None, description=None, group=None, visibility=None, users=None, **kwargs):
        if users is not None:
            users = [{"id": u_id} for u_id in users]

        if prefill:
            input = {int(c["id"]): c for c in self.init()["credentials"]}[int(id)]
        else:
            input = {"id": id}

        kwargs.update({
            "name": name,
            "type": type,
            "description": description,
            "group": group,
            "visibility": visibility,
            "users": users
        })
        kwargs = {key: value for key, value in kwargs.iteritems() if value is not None}
        input.update(kwargs)

        return self._request("edit", input)

    def edit_ssh(self, id, prefill=True, name=None, username=None, password=None, public_key=None, private_key=None, passphrase=None, escalation_type=None, escalation_username=None, escalation_password=None, description=None, group=None, visibility=None, users=None):
        if public_key is not None:
            public_key = self._sc.file.name_or_upload(public_key)

        if private_key is not None:
            private_key = self._sc.file.name_or_upload(private_key)

        return self.edit(
            id, prefill, name, "ssh", description, group, visibility, users,
            username=username, password=password,
            publicKey=public_key,
            privateKey=private_key, passphrase=passphrase,
            privilegeEscalation=escalation_type,
            escalationUsername=escalation_username,
            escalationPassword=escalation_password
        )

    def edit_windows(self, id, prefill=True, name=None, username=None, password=None, domain=None, description=None, group=None, visibility=None, users=None):
        return self.edit(id, prefill, name, "windows", description, group, visibility, users, username=username, password=password, domain=domain)

    def edit_snmp(self, id, prefill=True, name=None, community=None, description=None, group=None, visibility="user", users=None):
        return self.edit(id, prefill, name, "snmp", description, group, visibility, users, communityString=community)

    def edit_kerberos(self, id, prefill=True, name=None, ip=None, port=None, protocol=None, realm=None, description=None, group=None, visibility=None, users=None):
        return self.edit(id, prefill, name, "kerberos", description, group, visibility, users, ip=ip, port=port, protocol=protocol, realm=realm)

    def share_simulate(self, id, users):
        return self._request("shareSimulate", {
            "id": id,
            "users": [{"id": u_id} for u_id in users]
        })

    def share(self, id, users):
        return self._request("share", {
            "id": id,
            "users": [{"id": u_id} for u_id in users]
        })

    def delete_simulate(self, *ids):
        return self._request("deleteSimulate", {
            "credentials": [{"id": id} for id in ids]
        })

    def delete(self, *ids):
        return self._request("delete", {
            "credentials": [{"id": id} for id in ids]
        })


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


class File(Module):
    _name = "file"

    def upload(self, file, return_content=None):
        return self._request("upload", {"returnContent": return_content}, file)

    def clear(self, name):
        return self._request("clear", {"filename": name})

    # how to get existing files?

    def name_or_upload(self, data):
        if isinstance(data, basestring):
            return data

        r = self.upload(data, False)
        return r["filename"]


class Scan(Module):
    _name = "scan"

    def init(self):
        return self._request("init")

    def add(self):
        #TODO scan::add
        raise NotImplementedError

    def edit(self):
        #TODO scan::edit
        raise NotImplementedError

    def copy(self, id, name):
        return self._request("copy", {"id": id, "name": name})

    def delete_simulate(self, *ids):
        return self._request("deleteSimulate", {
            "scans": [{"id": s_id} for s_id in ids]
        })

    def delete(self, *ids):
        return self._request("delete", {
            "scans": [{"id": s_id} for s_id in ids]
        })

    def launch(self, id):
        return self._request("launch", {"scanID": id})

    def pause(self, result):
        return self._request("pause", {"scanResultID": result})

    def resume(self, result):
        return self._request("resume", {"scanResultID": result})

    def stop(self, result, type="discard"):
        # possible values for type: discard, import, rollover
        return self._request("stop", {"scanResultID": result, "type": type})


class ScanResult(Module):
    _name = "scanResult"

    def init(self):
        return self._request("init")

    def get_range(self, start=None, end=None, user=None):
        if isinstance(start, datetime):
            start = timegm(start.utctimetuple())

        if isinstance(end, datetime):
            end = timegm(end.utctimetuple())

        return self._request("getRange", {
            "startTime": start,
            "endTime": end,
            "userID": user
        })

    def get_progress(self, id):
        return self._request("getProgress", {"scanResultID": id})

    def download(self, id, type="v2"):
        r = self._request("download", {
            "scanResultID": id,
            "downloadType": type
        }, parse=False)

        z = ZipFile(StringIO(r.content))
        return z.read(z.namelist()[0])

    def import_(self, id, mitigated_age=None, track_ip=None, virtual=None):
        return self._request("import", {
            "scanResultID": id,
            "classifyMitigatedAge": mitigated_age,
            "dhcpTracking": track_ip,
            "scanningVirtualHosts": virtual
        })

    def delete(self, *ids):
        return self._request("delete", {
            "scanResults": [{"id": id} for id in ids]
        })


class NessusResults(Module):
    _name = "nessusResults"

    def upload(self, file, repo, mitigated_age=None, track_ip=None, virtual=None):
        filename = self._sc.file.name_or_upload(file)

        return self._request("upload", {
            "filename": filename,
            "repID": repo,
            "classifyMitigatedAge": mitigated_age,
            "dhcpTracking": track_ip,
            "scanningVirtualHosts": virtual
        })
