from base64 import b64decode
from calendar import timegm
from datetime import datetime
from .base import Module, extract_value


class Plugin(Module):
    _name = 'plugin'

    def _fetch(self, action, size, offset, since, type, sort, direction,
               filter_field, filter_string):
        if isinstance(since, datetime):
            since = timegm(since.utctimetuple())

        return self._request(action, {
            'size': size,
            'offset': offset,
            'type': type,
            'sortField': sort,
            'sortDirection': direction and direction.upper(),
            'filterField': filter_field,
            'filterString': filter_string,
            'since': since
        })

    @extract_value('plugins')
    def init(self, size=None, offset=None, since=None, type=None,
             sort=None, direction=None,
             filter_field=None, filter_string=None):
        return self._fetch('init', size, offset, since, type,
                           sort, direction, filter_field, filter_string)

    @extract_value('plugins')
    def get_page(self, size=None, offset=None, since=None, type=None,
                 sort=None, direction=None,
                 filter_field=None, filter_string=None):
        return self._fetch('getPage', size, offset, since, type,
                           sort, direction, filter_field, filter_string)

    def get_details(self, id):
        return self._request('getDetails', {'pluginID': id})['plugin']

    def get_source(self, id):
        """Returns the NASL source of a plugin.

        The API returns the script base64 encoded.  This is decoded
        and returned in plain text.

        If the script is encrypted, the result will say something about
        that instead of the source.

        :param id: plugin id
        :return:
        """
        return b64decode(self._request('getSource',
                                       {'pluginID': id})['source'])

    def get_families(self):
        return self._request('getFamilies')['families']

    def get_plugins(self, families):
        return self._request('getPlugins', {
            'families': [{'id': int(f_id)} for f_id in families]
        })['families']

    def update(self, type='all'):
        return self._request('update', {'type': type})

    def upload(self, data, type='custom'):
        filename = self._sc.file.name_or_upload(data)

        return self._request('upload', {'filename': filename, 'type': type})
