import json
from random import randint
from urlparse import urljoin
from requests import Session
from .exceptions import raise_for_error
from . import modules


class Client(object):
    """Open a connection to a Security Center instance.

    Provides the interface for making raw requests to the API.  Modules
    are registered on the connection object for performing actions in an
    easier format.

    If a username and password are provided, they will be used to
    log in after connecting.

    SSL is possible by passing a client certificate and a trust chain.
    When using two-way SSL with a client certificate, ``system.init``
    can cause an automatic log in if the certificate is registered.
    This can be disabled by setting ``_system_init`` to False.

    :param url: connect to a Security Center instance at this location.
            Must include scheme (https) and can include port (:443).
    :param username: after connecting, log in as this user, if given
    :param password: used for log in with username
    :param cert: path to client certificate for two-way SSL.  Can be a
            tuple of (cert, key) if they are separate.
    :param verify: how to verify host SSL cert.  If True, use system
            trust; if False, don't verify; otherwise, a path to a trust
            chain file.
    :param _system_init: whether to call ``system.init`` on connect
    """

    def __init__(self, url, username=None, password=None,
                 cert=None, verify=False, _system_init=True):
        # true endpoint is "request.php"
        self._url = urljoin(url, 'request.php')

        # set up session with SSL
        self._session = Session()
        self._session.cert = cert
        self._session.verify = verify

        # token returned after login
        self._token = None

        # register available modules, passing self as connection
        self.accept_risk_rules = modules.AcceptRiskRules(self)
        self.admin = modules.Admin(self)
        self.alert = modules.Alert(self)
        self.asset = modules.Asset(self)
        self.attribute_sets = modules.AttributeSet(self)
        self.auth = modules.Auth(self)
        self.credential = modules.Credential(self)
        self.daemon = modules.Daemons(self)
        self.file = modules.File(self)
        self.heartbeat = modules.Heartbeat(self)
        self.logging = modules.Logging(self)
        self.message = modules.Message(self)
        self.nessus_results = modules.NessusResults(self)
        self.org = modules.Organization(self)
        self.passive_scanner = modules.PassiveScanner(self)
        self.plugin = modules.Plugin(self)
        self.policy = modules.Policy(self)
        self.report = modules.Report(self)
        self.report_images = modules.ReportImages(self)
        self.report_result = modules.ReportResult(self)
        self.repository = modules.Repository(self)
        self.resource = modules.Resource(self)
        self.role = modules.Role(self)
        self.scan = modules.Scan(self)
        self.scanner = modules.Scanner(self)
        self.scan_result = modules.ScanResult(self)
        self.status = modules.Status(self)
        self.style = modules.Style(self)
        self.system = modules.System(self)
        self.ticket = modules.Ticket(self)
        self.user = modules.User(self)
        self.user_prefs = modules.UserPrefs(self)
        self.vuln = modules.Vuln(self)
        self.zone = modules.Zone(self)

        # try automatic login by client cert
        if _system_init:
            self.system.init()

        # try manual login by username
        if username is not None and password is not None:
            self.auth.login(username, password)

    def _request(self, module, action, input=None, file=None, parse=True):
        """Make an API call to the given module::action.

        :param module: name of module on server
        :param action: name of action in module
        :param input: any arguments to be passed to the module::action
        :type input: dict
        :param file: file data to upload
        :type file: file
        :param parse: if False, don't parse response as JSON

        :return: dict containing API response, or ``Response`` if parse
                is False
        """

        if input is None:
            input = {}

        # clean up input as SC expects it
        processed_input = {}
        for key, value in input.iteritems():
            if value is None:
                continue

            if isinstance(value, bool):
                # why does the server expect strings instead of bools?
                value = str(value).lower()

            processed_input[key] = value

        # make the request, and check for HTTP errors
        r = self._session.post(self._url, {
            'module': module,
            'action': action,
            'request_id': randint(10000, 20000),
            'token': self._token,
            'input': json.dumps(processed_input)
        }, files={'Filedata': file} if file else None)

        r.raise_for_status()

        # return response directly if not parsing
        if not parse:
            return r

        # parse json response and check for API errors
        j = self.parse_response(r)

        # may return an empty string or list instead of an error, but it's not
        # always an error

        return j['response']

    @staticmethod
    def parse_response(r):
        """Parse the response for errors and return the parsed JSON.

        Useful if you set ``parse`` to false in ``_request`` to get the whole
        JSON dict instead of the ``response`` value.

        :param r: response object with JSON body

        :return: entire parsed JSON body
        """

        j = r.json()
        raise_for_error(j)

        #TODO figure out what response types mean
        # only allow "regular" responses through
        # this could change if I figure out what other types really mean
        # if j['type'] != 'regular':
        #     # e.g. sc.plugin.get_plugins(families=[]) returns type='plugins'
        #     # instead of raising an error that it expects at least one family
        #     raise CoreError("Irregular response: {}".format(r.content))

        return j
