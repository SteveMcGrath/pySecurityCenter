from base import *

class User(Module):
    _name = "user"

    @extract_value("users")
    def init(self):
        return self._request("init")

    #TODO user