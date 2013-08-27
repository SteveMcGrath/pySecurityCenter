from base import *

class NessusResults(Module):
    _name = "nessusResults"

    def upload(self, file, repo, mitigated_age=None, track_ip=None, virtual=None):
        filename = self._sc.file.name_or_upload(file)

        return self._request("upload", {
            "filename": filename,
            "repID": repo,
            "classifyMitigatedAge": mitigated_age,
            "dhcpTracking": track_ip,
            "scanningVirtualHosts": virtual
        })