from base64 import b64decode
from cStringIO import StringIO
from calendar import timegm
from datetime import datetime
from functools import wraps
from zipfile import ZipFile


class Module(object):
    """API module that knows how to perform actions.

    :param sc: SecurityCenter connection
    """

    _name = ""
    """sc internal name of module"""

    def __init__(self, sc):
        self._sc = sc

    def _request(self, action, input=None, file=None, parse=True):
        """Make an API call to action under the current module.

        :param action: name of action in module
        :param input: any arguments to be passed to the module::action
        :type input: dict
        :param file: file data to upload
        :type file: file
        :param parse: if False, don't parse response as JSON

        :return: dict containing API response, or ``Response`` if parse
                is False
        """

        return self._sc._request(self._name, action, input, file, parse)


class _Empty(object):
    pass


def extract_value(key, default=_Empty, _all_key="_all"):
    """Extract the value of a key from a returned dict.

    Creates a decorator that will get the value of a key from a function
    returning a dictionary.

    When calling the decorated function, set ``_all`` to True to make
    this a no-op and return the entire dictionary.

    If the function requires that ``_all`` is set for some input, add
    the key _all to the returned dictionary.  For example, normally
    return a filename, but if called as ``f(..., verbose=True)``,
    return the file stats also.

    :param key: key to get from return
    :param default: if set, return this if key is not present, otherwise
            raise KeyError
    :param _all_key: name of param for "_all_" behavior (default "_all")

    :raise KeyError: if key not in dict and no default

    :return: extracted value
    """

    #TODO use generator send() to allow pre- and post-processing?

    def decorator(f):
        @wraps(f)
        def inner(*args, **kwargs):
            no_extract = kwargs.pop(_all_key, False)
            res = f(*args, **kwargs)
            no_extract = res.pop(_all_key, no_extract)
            if no_extract:
                return res
            if default is _Empty:
                return res.get(key)
            return res.get(key, default)
        return inner
    return decorator


class System(Module):
    _name = "system"

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

            r = self._request("init")
        finally:
            # make sure to restore the auth token
            self._sc._token = token

        token = r.get("token")

        if token:
            # new token, log out of the old session and set
            if self._sc._token:
                self._sc.auth.logout()

            self._sc._token = token

        return r


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

    @extract_value("filename")
    def upload(self, file, return_content=None):
        """Upload a file for use in import functions.

        :param file: file-like object open for reading
        :type file: file
        :param return_content: whether to return the uploaded data as
                part of the response
        :return: random name assigned to file
        """

        res = self._request("upload", {"returnContent": return_content}, file)
        if return_content:
            res["_all"] = True
        return res

    def clear(self, name):
        """Delete a file previously uploaded.

        :param name: name of file returned after upload
        :return: path of deleted file
        """

        return self._request("clear", {"filename": name})["filename"]

    # how to get existing files?

    def name_or_upload(self, data):
        """If data is a string, assume it's a filename and return it;
        otherwise assume it's a file, upload it, and return the
        generated filename.

        This is useful inside import functions to allow new and existing
        files.

        :param data: filename or file-like object to upload
        :return: filename
        """

        if isinstance(data, basestring):
            return data

        return self.upload(data, False)


class Auth(Module):
    _name = "auth"

    def login(self, username, password):
        """Authenticate with username and password."""

        # log out if already logged in
        if self._sc._token:
            self.logout()

        res = self._request("login", {
            "username": username,
            "password": password
        })

        self._sc._token = res["token"]

        return res

    def logout(self):
        """Clear the auth data from the server and client."""

        try:
            return self._request("logout")
        finally:
            # if the user was timed out, the request will fail, but we
            # still need to clear the auth data
            self._sc._token = None
            self._sc._session.cookies.clear()

    def save_fingerprint(self):
        """When using two-way SSL, this stores the client cert to enable
        automatic login without a username/password."""

        return self._request("saveFingerprint")


class Plugin(Module):
    _name = "plugin"

    def _fetch(self, action, size, offset, since, type, sort, direction, filter_field, filter_string):
        if isinstance(since, datetime):
            since = timegm(since.utctimetuple())

        return self._request(action, {
            "size": size,
            "offset": offset,
            "type": type,
            "sortField": sort,
            "sortDirection": direction and direction.upper(),
            "filterField": filter_field,
            "filterString": filter_string,
            "since": since
        })

    @extract_value("plugins")
    def init(self, size=None, offset=None, since=None, type=None, sort=None, direction=None, filter_field=None, filter_string=None):
        return self._fetch("init", size, offset, since, type, sort, direction, filter_field, filter_string)

    @extract_value("plugins")
    def get_page(self, size=None, offset=None, since=None, type=None, sort=None, direction=None, filter_field=None, filter_string=None):
        return self._fetch("getPage", size, offset, since, type, sort, direction, filter_field, filter_string)

    def get_details(self, id):
        return self._request("getDetails", {"pluginID": id})["plugin"]

    def get_source(self, id):
        """Returns the NASL source of a plugin.

        The API returns the script base64 encoded.  This is decoded
        and returned in plain text.

        If the script is encrypted, the result will say something about
        that instead of the source.

        :param id: plugin id
        :return:
        """
        return b64decode(self._request("getSource", {"pluginID": id})["source"])

    def get_families(self):
        return self._request("getFamilies")["families"]

    def get_plugins(self, families):
        return self._request("getPlugins", {
            "families": [{"id": int(f_id)} for f_id in families]
        })["families"]

    def update(self, type="all"):
        return self._request("update", {"type": type})

    def upload(self, data, type="custom"):
        filename = self._sc.file.name_or_upload(data)

        return self._request("upload", {"filename": filename, "type": type})


class Credential(Module):
    _name = "credential"

    @extract_value("credentials")
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
            if isinstance(prefill, bool):
                input = dict((int(c["id"]), c) for c in self.init()["credentials"])[int(id)]
            else:
                input = dict(prefill)
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
        kwargs = dict((key, value) for key, value in kwargs.iteritems() if value is not None)
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
        })["effects"]

    def share(self, id, users):
        return self._request("share", {
            "id": id,
            "users": [{"id": u_id} for u_id in users]
        })

    def delete_simulate(self, *ids):
        return self._request("deleteSimulate", {
            "credentials": [{"id": id} for id in ids]
        })["effects"]

    def delete(self, *ids):
        return self._request("delete", {
            "credentials": [{"id": id} for id in ids]
        })["credentials"]


class Scan(Module):
    _name = "scan"

    @extract_value("scans")
    def init(self):
        return self._request("init")

    @extract_value("scan")
    def add(self, name, repo, description=None, freq="template", when=None,
            assets=None, ips=None, policy=None, plugin=None, zone=None,
            credentials=None, mail_launch=None, mail_finish=None,
            mitigated_age=None, track_ip=None, virtual=None, timeout=None,
            reports=None):

        assets = assets or []
        ips = ips or []
        credentials = credentials or []
        reports = reports or []

        if plugin is not None:
            type = "plugin"
            policyID = None
        else:
            type = "policy"
            policyID = policy
            policy = None

        return self._request("add", {
            "name": name, "description": description, "repositoryID": repo,
            "scheduleFrequency": freq, "scheduleDefinition": when,
            "assets": [{"id": a_id} for a_id in assets], "ipList": ips,
            "type": type, "policyID": policyID, "policy": policy,
            "pluginID": plugin, "zoneID": zone,
            "credentials": [{"id": c_id} for c_id in credentials],
            "emailOnLaunch": mail_launch, "emailOnFinish": mail_finish,
            "classifyMitigatedAge": mitigated_age, "dhcpTracking": track_ip,
            "scanningVirtualHosts": virtual, "timeout": timeout,
            "reports": [{"id": r_id} for r_id in reports]
        })

    def edit(self):
        #TODO scan::edit
        raise NotImplementedError

    @extract_value("scan")
    def copy(self, id, name):
        return self._request("copy", {"id": id, "name": name})

    def delete_simulate(self, *ids):
        return self._request("deleteSimulate", {
            "scans": [{"id": s_id} for s_id in ids]
        })["effects"]

    def delete(self, *ids):
        return self._request("delete", {
            "scans": [{"id": s_id} for s_id in ids]
        })["scans"]

    @extract_value("scanResult")
    def launch(self, id):
        return self._request("launch", {"scanID": id})

    def pause(self, result):
        return self._request("pause", {"scanResultID": result})["scanResults"]

    def resume(self, result):
        return self._request("resume", {"scanResultID": result})["scanResults"]

    def stop(self, result, type="discard"):
        # possible values for type: discard, import, rollover
        return self._request("stop", {"scanResultID": result, "type": type})


class ScanResult(Module):
    _name = "scanResult"

    @extract_value("scanResults")
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
        })["scanResults"]

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
        })["scanResults"]


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


class Policy(Module):
    _name = "policy"

    @extract_value("policies")
    def init(self):
        return self._request("init")

    def add(self):
        #TODO policy::add
        raise NotImplementedError

    def edit(self):
        #TODO policy::edit
        raise NotImplementedError

    def share_simulate(self, id, users):
        return self._request("shareSimulate", {
            "id": id,
            "users": [{"id": u_id} for u_id in users]
        })["effects"]

    def share(self, id, users):
        return self._request("share", {
            "id": id,
            "users": [{"id": u_id} for u_id in users]
        })

    def copy(self, id, name):
        return self._request("copy", {"id": id, "name": name})

    def delete_simulate(self, *ids):
        return self._request("deleteSimulate", {
            "policies": [{"id": id} for id in ids]
        })["effects"]

    def delete(self, *ids):
        return self._request("delete", {
            "policies": [{"id": id} for id in ids]
        })["policies"]

    def download(self, id):
        return self._request("exportNessusPolicy", {"id": id}, parse=False).content

    def upload(self, file, name=None, visibility="user", description=None, group=None):
        #TODO parse xml to fill other fields
        filename = self._sc.file.name_or_upload(file)

        return self._request("importNessusPolicy", {
            "filename": filename,
            "name": name,
            "visibility": visibility,
            "description": description,
            "group": group
        })


class Vuln(Module):
    _name = "vuln"

    def init(self):
        return self._request("init")

    @extract_value("results")
    def query(self, tool, source="cumulative", size=None, offset=None, sort=None, direction=None, scan=None, view=None, filters=None, **filter_by):
        # source cumulative, patched, individual
        # directory YYYY-MM-DD from scan finish time, required but ignored by server
        # view all, patched, or new

        if scan is not None:
            source = "individual"

            if view is None:
                view = "all"

        if filters is None:
            filters = []

        for key, value in filter_by.iteritems():
            filters.append({
                "filterName": key,
                "operator": "=",
                "value": value
            })

        if size is not None and offset is not None:
            end = offset + size
        else:
            end = None

        return self._request("query", {
            "tool": tool, "sourceType": source,
            "startOffset": offset, "endOffset": end,
            "sortField": sort, "sortDir": direction and direction.upper(),
            "filters": filters,
            "view": view, "dateDirectory": "null", "scanID": scan
        })

    def download(self):
        #TODO vuln::download
        raise NotImplementedError

    @extract_value("records")
    def get_ip(self, ip, repos=None):
        if repos is not None:
            repos = [{"id": r_id} for r_id in repos]

        return self._request("getIP", {
            "ip": ip,
            "repositories": repos
        })


class Report(Module):
    _name = "report"

    @extract_value("reports")
    def init(self):
        return self._request("init")

    def add(self):
        #TODO report::add
        raise NotImplementedError

    def edit(self):
        #TODO report::edit
        raise NotImplementedError

    def copy(self, id, name):
        return self._request("copy", {"id": id, "name": name})

    def delete(self, *ids):
        return self._request("delete", {
            "reports": [{"id": id} for id in ids]
        })["reports"]

    def export(self, id, type="cleansed"):
        # type is cleansed, full, or placeholders
        return self._request("export", {"id": id, "exportType": type}, parse=False).content

    def import_(self, file, name=None):
        filename = self._sc.file.name_or_upload(file)
        return self._request("import", {"filename": filename, "name": name})

    @extract_value("reportResult")
    def launch(self, id):
        return self._request("launch", {"id": id})

    def stop(self, result):
        return self._request("stop", {"reportResultID": result})


class ReportResult(Module):
    _name = "reportResult"

    @extract_value("reportResults")
    def init(self):
        return self._request("init")

    @extract_value("reportResults")
    def get_range(self, start=None, end=None):
        if isinstance(start, datetime):
            start = timegm(start.utctimetuple())

        if isinstance(end, datetime):
            end = timegm(end.utctimetuple())

        return self._request("getRange", {
            "startTime": start,
            "endTime": end
        })

    def download(self, id):
        return self._request("download", {"reportResultID": id}, parse=False).content

    def share(self, ids, users=None, emails=None):
        return self._request("share", {
            "resultID": ids,
            "userID": users,
            "email": emails
        })

    def send(self):
        #TODO report::send
        raise NotImplementedError

    def delete(self, *ids):
        return self._request("delete", {
            "reportResults": [{"id": id} for id in ids]
        })["reportResults"]


class Asset(Module):
    _name = "asset"

    @extract_value("assets")
    def init(self):
        return self._request("init")

    @extract_value("viewable_ips")
    def get_ips(self, id, ips_only=False):
        return self._request("getIPs", {
            "id": id,
            "ipsOnly": int(ips_only)
        })

    def combine(self, ids, ips, operator):
        # operator is union, intersection, difference, or complement
        return self._request("combine", {
            "assetIDs": [{"id": id} for id in ids],
            "definedIPs": ips,
            "operator": operator
        })

    def add(self):
        #TODO asset::add
        raise NotImplementedError

    def edit(self):
        #TODO asset::edit
        raise NotImplementedError

    def share_simulate(self, id, users):
        return self._request("shareSimulate", {
            "id": id,
            "users": [{"id": u_id} for u_id in users]
        })["effects"]

    def share(self, id, users):
        return self._request("share", {
            "id": id,
            "users": [{"id": u_id} for u_id in users]
        })

    def delete_simulate(self, *ids):
        return self._request("deleteSimulate", {
            "assets": [{"id": id} for id in ids]
        })["effects"]

    def delete(self, *ids):
        return self._request("delete", {
            "assets": [{"id": id} for id in ids]
        })["assets"]


class Repository(Module):
    _name = "repository"

    @extract_value("repositories")
    def init(self):
        return self._request("init")

    #TODO repository


class Zone(Module):
    _name = "zone"

    @extract_value("zones")
    def init(self):
        return self._request("init")

    #TODO: zone


class User(Module):
    _name = "user"

    @extract_value("users")
    def init(self):
        return self._request("init")

    #TODO user


class Admin(User):
    _name = "admin"

    #TODO? admin


class Role(Module):
    _name = "role"

    @extract_value("roles")
    def init(self):
        return self._request("init")

    #TODO role
