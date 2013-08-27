from base import *

class Role(Module):
    _name = "role"

    @extract_value("roles")
    def init(self):
        return self._request("init")

    #TODO role