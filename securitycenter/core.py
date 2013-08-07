import json
from random import randint
from urlparse import urljoin
from requests import Session
from . import modules
from .exc import raise_for_error, CoreError


class SecurityCenter(object):
    def __init__(self, url, username=None, password=None, cert=None, verify=False, _system_init=True):
        self._url = urljoin(url, "request.php")

        self._session = Session()
        self._session.cert = cert
        self._session.verify = verify

        self._token = None

        self.auth = modules.Auth(self)
        self.credential = modules.Credential(self)
        self.file = modules.File(self)
        self.heartbeat = modules.Heartbeat(self)
        self.message = modules.Message(self)
        self.nessus_results = modules.NessusResults(self)
        self.plugin = modules.Plugin(self)
        self.policy = modules.Policy(self)
        self.scan = modules.Scan(self)
        self.scan_result = modules.ScanResult(self)
        self.system = modules.System(self)

        if _system_init:
            self.system.init()

        if username is not None and password is not None:
            self.auth.login(username, password)

    def _request(self, module, action, input=None, file=None, parse=True):
        if input is None:
            input = {}

        processed_input = {}
        for key, value in input.iteritems():
            if value is None:
                continue

            if isinstance(value, bool):
                value = str(value).lower()

            processed_input[key] = value

        r = self._session.post(self._url, {
            "module": module,
            "action": action,
            "request_id": randint(10000, 20000),
            "token": self._token,
            "input": json.dumps(processed_input)
        }, files={"Filedata": file} if file else None)

        r.raise_for_status()

        if not parse:
            return r

        j = r.json()
        raise_for_error(j)

        if j["type"] != "regular":
            # e.g. sc.plugin.get_plugins(families=[]) returns type="plugins"
            # instead of raising an error that it expects at least one family
            raise CoreError("Irregular response: {}".format(r.content))

        # may return an empty string or list instead of an error, but it's not
        # always an error

        return j["response"]
