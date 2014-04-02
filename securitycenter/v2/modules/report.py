from calendar import timegm
from datetime import datetime
from .base import Module, extract_value


class Report(Module):
    _name = 'report'

    @extract_value('reports')
    def init(self):
        return self._request('init')

    def add(self):
        #TODO report::add
        raise NotImplementedError

    def edit(self):
        #TODO report::edit
        raise NotImplementedError

    def copy(self, id, name):
        return self._request('copy', {'id': id, 'name': name})

    def delete(self, *ids):
        return self._request('delete', {
            'reports': [{'id': id} for id in ids]
        })['reports']

    def export(self, id, type='cleansed'):
        # type is cleansed, full, or placeholders
        return self._request('export', {
            'id': id, 'exportType': type
        }, parse=False).content

    def import_(self, file, name=None):
        filename = self._sc.file.name_or_upload(file)
        return self._request('import', {'filename': filename, 'name': name})

    @extract_value('reportResult')
    def launch(self, id):
        return self._request('launch', {'id': id})

    def stop(self, result):
        return self._request('stop', {'reportResultID': result})


class ReportResult(Module):
    _name = 'reportResult'

    @extract_value('reportResults')
    def init(self):
        return self._request('init')

    @extract_value('reportResults')
    def get_range(self, start=None, end=None):
        if isinstance(start, datetime):
            start = timegm(start.utctimetuple())

        if isinstance(end, datetime):
            end = timegm(end.utctimetuple())

        return self._request('getRange', {
            'startTime': start,
            'endTime': end
        })

    def download(self, id):
        return self._request('download', {
            'reportResultID': id
        }, parse=False).content

    def share(self, ids, users=None, emails=None):
        return self._request('share', {
            'resultID': ids,
            'userID': users,
            'email': emails
        })

    def send(self):
        #TODO report::send
        raise NotImplementedError

    def delete(self, *ids):
        return self._request('delete', {
            'reportResults': [{'id': id} for id in ids]
        })['reportResults']


class ReportImages(Module):
    _name = 'reportImages'

    @extract_value('reportImages')
    def init(self):
        return self._request('init')

    def add(self):
        #TODO: reportImages::add
        raise NotImplementedError

    def edit(self):
        #TODO: reportImages::edit
        raise NotImplementedError

    def delete(self, images):
        """Deletes specified report images.

        :param images: reportImages

        :return param
        """
        return self._request('delete', {
            'reportImages': images
        })

    def get_details(self):
        #TODO: reportImages::get_details
        raise NotImplementedError