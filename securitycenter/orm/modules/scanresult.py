from base import *

class ScanResult(Module):
    _name = "scanResult"

    @extract_value("scanResults")
    def init(self):
        return self._request("init")

    def get_range(self, start=None, end=None, user=None):
        if isinstance(start, datetime):
            start = timegm(start.utctimetuple())

        if isinstance(end, datetime):
            end = timegm(end.utctimetuple())

        return self._request("getRange", {
            "startTime": start,
            "endTime": end,
            "userID": user
        })["scanResults"]

    def get_progress(self, id):
        return self._request("getProgress", {"scanResultID": id})

    def download(self, id, type="v2"):
        r = self._request("download", {
            "scanResultID": id,
            "downloadType": type
        }, parse=False)

        z = ZipFile(StringIO(r.content))
        return z.read(z.namelist()[0])

    def import_(self, id, mitigated_age=None, track_ip=None, virtual=None):
        return self._request("import", {
            "scanResultID": id,
            "classifyMitigatedAge": mitigated_age,
            "dhcpTracking": track_ip,
            "scanningVirtualHosts": virtual
        })

    def delete(self, *ids):
        return self._request("delete", {
            "scanResults": [{"id": id} for id in ids]
        })["scanResults"]