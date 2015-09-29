from .base import BaseAPI, APIError, logging


class Nessus(BaseAPI):
    _access = None
    _secret = None
    def __init__(self, host, port=8834, ssl_verify=False, scheme='https', log=False):
        BaseAPI.__init__(self, host, port, ssl_verify, scheme, log)
        try:
            d = self.get('server/properties')
            self.type = d['nessus_type']
            self.version = d['server_version']
            self.ui_build = d['nessus_ui_build']
            self.ui_version = d['nessus_ui_version']
            self.build = d['server_build']
        except:
            raise APIError(404, 'Invalid Nessus Instance')

    def _builder(self, **kwargs):
        kwargs = BaseAPI._builder(self, **kwargs)
        if self._access and self._secret:
            kwargs['headers']['X-APIKeys'] = 'accessKey=%s secretKey=%s' % (self._access, self._secret)
        elif self._token:
            kwargs['headers']['X-Cookie'] = 'token=%s' % self._token
        return kwargs

    def login(self, username=None, password=None, access=None, secret=None):
        if username and password:
            resp = self.post('session', json={'username': username, 'password': password})
            if resp.status == 200:
                self._token = resp.json()['token']
            else:
                raise APIError(resp.status, resp.json()['error'])
        elif access and secret:
            self._access = access
            self._secret = secret
        else:
            raise APIError(404, 'No Authentication Methods Found')


