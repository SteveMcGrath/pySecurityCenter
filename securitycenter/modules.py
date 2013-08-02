class Module(object):
    def __init__(self, sc):
        self.sc = sc


class System(Module):
    def init(self):
        r = self.sc._request("system", "init")

        token = r.get("token")

        if token:
            if self.sc._token:
                self.sc.auth.logout()

            self.sc._token = token

        return r


class Auth(Module):
    def login(self, username, password):
        if self.sc._token:
            self.logout()

        r = self.sc._request("auth", "login", {
            "username": username,
            "password": password
        })

        self.sc._token = r["token"]

        return r

    def logout(self):
        r = self.sc._request("auth", "logout")

        self.sc._token = None
        self.sc._session.cookies.clear()

        return r

    def save_fingerprint(self):
        return self.sc._request("auth", "saveFingerprint")
