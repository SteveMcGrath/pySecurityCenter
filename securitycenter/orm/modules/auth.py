from .base import Module


class Auth(Module):
    _name = 'auth'

    def login(self, username, password):
        """Authenticate with username and password."""

        # log out if already logged in
        if self._sc._token:
            self.logout()

        res = self._request('login', {
            'username': username,
            'password': password
        })

        self._sc._token = res['token']

        return res

    def logout(self):
        """Clear the auth data from the server and client."""

        try:
            return self._request('logout')
        finally:
            # if the user was timed out, the request will fail, but we
            # still need to clear the auth data
            self._sc._token = None
            self._sc._session.cookies.clear()

    def save_fingerprint(self):
        """When using two-way SSL, this stores the client cert to enable
        automatic login without a username/password."""

        return self._request('saveFingerprint')
