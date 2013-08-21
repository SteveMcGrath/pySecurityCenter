from base import *

class ReportResult(Module):
    _name = "reportResult"

    @extract_value("reportResults")
    def init(self):
        return self._request("init")

    @extract_value("reportResults")
    def get_range(self, start=None, end=None):
        if isinstance(start, datetime):
            start = timegm(start.utctimetuple())

        if isinstance(end, datetime):
            end = timegm(end.utctimetuple())

        return self._request("getRange", {
            "startTime": start,
            "endTime": end
        })

    def download(self, id):
        return self._request("download", {"reportResultID": id}, parse=False).content

    def share(self, ids, users=None, emails=None):
        return self._request("share", {
            "resultID": ids,
            "userID": users,
            "email": emails
        })

    def send(self):
        #TODO report::send
        raise NotImplementedError

    def delete(self, *ids):
        return self._request("delete", {
            "reportResults": [{"id": id} for id in ids]
        })["reportResults"]