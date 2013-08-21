from base import *

class Zone(Module):
    _name = "zone"

    @extract_value("zones")
    def init(self):
        return self._request("init")

    #TODO: zone