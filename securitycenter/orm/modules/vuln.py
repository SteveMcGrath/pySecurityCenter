from .base import Module, extract_value


class Vuln(Module):
    _name = 'vuln'

    def init(self):
        return self._request('init')

    def validate_params(self, user_id, org_id, start_offset, end_offset,
        tool=None, source_type=None, view=None, date_directory=None, scan_id=None):
        """Validate the parameters.

        :param user_id: the user's id
        :param org_id: the org's id
        :param start_offset: the numeric value for starting record
        :param end_offset: the numeric value for ending record
        :param tool: the tool to be used for the query
        :param source_type: the source type
        :param view: a view for the individual data source
        :param date_directory: a date directory for data source
        :param scan_id: scan id for data source

        :return: return values
        """

        if source_type is not None:
            self.view = view
            self.date_directory = date_directory
            self.scan_id = scan_id

        return self._request('validateParams', {
            'userId': user_id,
            'orgID': org_id,
            'tool': tool,
            'startOffset': start_offset,
            'endOffset': end_offset,
            'sourceType': source_type,
            'view': view,
            'dateDirectory': date_directory,
            'scanID': scan_id
        })

    def scrub_params(self, filters):
        """Perform input scrubbing by removing whitespace and new lines.

        :param filters: identify what will be scrubbed

        :return: return array scrubbed params
        """

        return self._request('scrubParams', {
            'filters': filters
        })

    @extract_value('results')
    def query(self, tool, source='cumulative', size=None, offset=None,
              sort=None, direction=None, scan=None, view=None,
              filters=None, **filter_by):
        # source cumulative, patched, individual
        # directory YYYY-MM-DD from scan finish time
        #     required but ignored by server
        # view all, patched, or new

        if scan is not None:
            source = 'individual'

            if view is None:
                view = 'all'

        if filters is None:
            filters = []

        for key, value in filter_by.iteritems():
            filters.append({
                'filterName': key,
                'operator': '=',
                'value': value
            })

        if size is not None:
            start = offset or 0
            end = start + size
        else:
            start, end = None, None

        input = {
            'tool': tool, 'sourceType': source,
            'startOffset': start, 'endOffset': end,
            'sortField': sort, 'sortDir': direction and direction.upper(),
            'filters': filters,
            'view': view, 'dateDirectory': 'null', 'scanID': scan
        }

        if tool in ('vulndetails', 'listvuln') and size is None:
            start, end = 0, 1000
            input['startOffset'] = start
            input['endOffset'] = end
            out = self._request('query', input)
            results = out['results']
            total = int(out['totalRecords'])
            while end < total:
                start, end = end, end + 1000
                input['startOffset'] = start
                input['endOffset'] = end
                results.extend(self._request('query', input)['results'])
            return out

        return self._request('query', input)

    @extract_value('records')
    def get_ip(self, ip, repos=None):
        if repos is not None:
            repos = [{'id': r_id} for r_id in repos]

        return self._request('getIP', {
            'ip': ip,
            'repositories': repos
        })

    def get_asset_data(self, id):
        """Gets the details of a given asset.

        :param id: id must be set and a valid asset id

        :return: returns full details for a given asset
        """

        return self._request('getAssetData', {
            'id': id
        })

    def download(self):
        #TODO vuln::download
        raise NotImplementedError

    def get_asset_intersections(self, ip, asset_id, dns_name, repos):
        #TODO vuln::getAssetIntersections
        raise NotImplementedError
