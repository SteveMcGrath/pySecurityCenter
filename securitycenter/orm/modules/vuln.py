from base import *

class Vuln(Module):
    _name = "vuln"

    def init(self):
        return self._request("init")

    @extract_value("results")
    def query(self, tool, source="cumulative", size=None, offset=None, sort=None, direction=None, scan=None, view=None, filters=None, **filter_by):
        # source cumulative, patched, individual
        # directory YYYY-MM-DD from scan finish time, required but ignored by server
        # view all, patched, or new

        if scan is not None:
            source = "individual"

            if view is None:
                view = "all"

        if filters is None:
            filters = []

        for key, value in filter_by.iteritems():
            filters.append({
                "filterName": key,
                "operator": "=",
                "value": value
            })

        if size is not None:
            start = offset or 0
            end = start + size
        else:
            start, end = None, None

        input = {
            "tool": tool, "sourceType": source,
            "startOffset": start, "endOffset": end,
            "sortField": sort, "sortDir": direction and direction.upper(),
            "filters": filters,
            "view": view, "dateDirectory": "null", "scanID": scan
        }

        if tool in ("vulndetails", "listvuln") and size is None:
            start, end = 0, 1000
            input["startOffset"] = start
            input["endOffset"] = end
            out = self._request("query", input)
            results = out["results"]
            total = int(out["totalRecords"])
            while end < total:
                start, end = end, end + 1000
                input["startOffset"] = start
                input["endOffset"] = end
                results.extend(self._request("query", input)["results"])
            return out

        return self._request("query", input)

    def download(self):
        #TODO vuln::download
        raise NotImplementedError

    @extract_value("records")
    def get_ip(self, ip, repos=None):
        if repos is not None:
            repos = [{"id": r_id} for r_id in repos]

        return self._request("getIP", {
            "ip": ip,
            "repositories": repos
        })