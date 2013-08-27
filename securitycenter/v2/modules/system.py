from base import *

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