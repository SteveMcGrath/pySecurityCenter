from base import *

class Report(Module):
    _name = "report"

    @extract_value("reports")
    def init(self):
        return self._request("init")

    def add(self):
        #TODO report::add
        raise NotImplementedError

    def edit(self):
        #TODO report::edit
        raise NotImplementedError

    def copy(self, id, name):
        return self._request("copy", {"id": id, "name": name})

    def delete(self, *ids):
        return self._request("delete", {
            "reports": [{"id": id} for id in ids]
        })["reports"]

    def export(self, id, type="cleansed"):
        # type is cleansed, full, or placeholders
        return self._request("export", {"id": id, "exportType": type}, parse=False).content

    def import_(self, file, name=None):
        filename = self._sc.file.name_or_upload(file)
        return self._request("import", {"filename": filename, "name": name})

    @extract_value("reportResult")
    def launch(self, id):
        return self._request("launch", {"id": id})

    def stop(self, result):
        return self._request("stop", {"reportResultID": result})