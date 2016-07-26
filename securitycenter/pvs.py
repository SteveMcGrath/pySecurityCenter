from .base import BaseAPI, APIError, logging


class PVS(BaseAPI):
    def __init__(self, host, port=8835, ssl_verify=False, scheme='https', log=False):
        BaseAPI.__init__(self, host, port, ssl_verify, scheme, log)

    def _builder(self, **kwargs):
        kwargs = BaseAPI._builder(self, **kwargs)
        return kwargs

    def login(self, username, password):
        resp = self.post('login', data={
                'login': username,
                'password': password,
                'json': 1,
        })
        if resp.status_code == 200:
            self._token = resp.json()['reply']['contents']['token']
        else:
            try:
                raise APIError(resp.status_code, resp.json())
            except:
                print(resp.content)

    def logout(self):
        self.post('logout', data={
            'json': 1,
            'token': self._token
        })
        self._reset_session()
