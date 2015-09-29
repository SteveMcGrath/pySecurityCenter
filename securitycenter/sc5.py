from .base import BaseAPI, APIError, logging


class SecurityCenter5(BaseAPI):
    _cookies = {}
    _pre = 'rest/'
    def __init__(self, host, port=443, ssl_verify=False, scheme='https', log=False):
        '''SecurityCenter 5 API Wrapper
        This class is designed to handle authentication management for the
        SecurityCenter 5.x API.  This is by no means a complete model of
        everything that the API can handle, it is simply meant to be a thin
        wrapper into the API.  Convenience functions will be added as time
        passes and there is a desire to develop them.

        For more information, please See Tenable's official API documentation
        at: https://support.tenable.com/support-center/cerberus-support-center/includes/widgets/sc_api/index.html
        '''
        BaseAPI.__init__(self, host, port, ssl_verify, scheme, log)
        d = self.get('system').json()
        self.version = d['response']['version']
        self.build_id = d['response']['buildID']
        self.license = d['response']['licenseStatus']
        self.uuid = d['response']['uuid']
        #raise APIError(404, 'Invalid SecurityCenter Instance')

    def _resp_error_check(self, response):
        try:
            d = response.json()
            if d['error_code']:
                raise APIError(d['error_code'], d['error_msg'])
        except ValueError:
            pass
        return response

    def _builder(self, **kwargs):
        kwargs = BaseAPI._builder(self, **kwargs)
        if self._token:
            kwargs['headers']['X-SecurityCenter'] = self._token
        kwargs['cookies'] = self._cookies
        return kwargs

    def login(self, user, passwd):
        '''Logs the user into SecurityCenter and stores the needed token and cookies.'''
        resp = self.post('token', json={'username': user, 'password': passwd})
        self._token = resp.json()['response']['token']
        self._cookies['TNS_SESSIONID'] = resp.cookies['TNS_SESSIONID']

    def logout(self):
        '''Logs out of SecurityCenter and removed the cookies and token.'''
        resp = self.delete('token')
        self._token = None
        self._cookies = {}

    def analysis(self, *filters, **kwargs):
        '''Analysis
        A thin wrapper to handle vuln/event/mobile/log analysis through the API.  This
        function handles expanding multiple filters and will translate arbitrary arguments
        into the format that SecurityCenter's analysis call expect them to be in.

        In order to make the filter expander more useful for SecurityCenter5 verses the
        SecurityCenter4 class, filters are no longer done as kwargs, and instead are done
        as a list of tuples.  For example, to get the IP Summary of all of the hosts in
        the 10.10.0.0/16 network, we would make the following call:

        vulns = sc.analysis(('ip','=','10.10.0.0/16'), tool='sumip')

        If multiple filters are desired, then it's simply a matter of entering multiple tuples.

        The Analysis function also has a few functions that are sligly deviated from the API
        guides.  All of these options are optional, however can significantly change the how
        the API is being called.

        page         - Default "all"                The current page in the pagination sequence.
        page_size    - Default 1000                 The page size (number of returned results)
        page_obj     - Default "return_results"     The class thats called after every API pull.
        page_kwargs  - Default {}                   Any additional arguments that need to be passed
                                                    to the page_obj class when instantiated.
        type         - Default "vuln"               This is the type of data that will be returned.
                                                    As all of the LCE and Vuln calls have been
                                                    collapsed into "analysis" in the API, each filter
                                                    needs to have these specified.  This module does
                                                    that legwork for you.
        sourceType   - Default "cumulative"         This is how we specify individual scans, LCE archive
                                                    silos, and other datasets that stand outside the norm.
        '''
        output = []
        def return_results(**kwargs):
            return kwargs['resp'].json()['response']['results']

        # These values are commonly used and/or are generally not changed from the default.  
        # If we do not see them specified by the user then we will need to add these in
        # for later parsing...
        if 'page' not in kwargs: kwargs['page'] = 'all'
        if 'page_size' not in kwargs: kwargs['page_size'] = 1000
        if 'page_obj' not in kwargs: kwargs['page_obj'] = return_results
        if 'page_kwargs' not in kwargs: kwargs['page_kwargs'] = {}
        if 'type' not in kwargs: kwargs['type'] = 'vuln'
        if 'sourceType' not in kwargs: kwargs['sourceType'] = 'cumulative'

        # New we need to pull out the options from kwargs as we will be using hwargs as
        # the basis for the query that will be sent to SecurityCenter.
        opts = {}
        for opt in ['page', 'page_size', 'page_obj', 'page_kwargs']:
            opts[opt] = kwargs[opt]
            del kwargs[opt]

        # If a query option was not set, then we will have to.  The hope here is that
        # we can make a lot of the pain of building the query pretty easy by simply
        # accepting tuples of the filters.
        if 'query' not in kwargs:
            kwargs['query'] = {
                'tool': kwargs['tool'],
                'type': kwargs['type'],
                'filters': [{'filterName': f[0], 'operator': f[1], 'value': f[2], 'type': kwargs['type']} for f in filters]
            }
            del kwargs['tool']
            if opts['page'] == 'all':
                kwargs['query']['startOffset'] = 0
                kwargs['query']['endOffset'] = opts['page_size']
            else:
                kwargs['query']['startOffset'] = opts['page'] * opts['page_size']
                kwargs['query']['endOffset'] = (opts['page'] + 1) * opts['page_size']

        count = 0
        total_records = opts['page_size']
        while total_records > count:
            # Here we actually make the calls.  
            resp = self.post('analysis', json=kwargs)
            opts['page_kwargs']['resp'] = resp
            out = opts['page_obj'](**opts['page_kwargs'])
            if isinstance(out, list):
                for item in out:
                    output.append(item)
            total_records = int(resp.json()['response']['totalRecords'])
            if opts['page'] == 'all':
                count = int(resp.json()['response']['endOffset'])
                kwargs['query']['startOffset'] = count
                kwargs['query']['endOffset'] = count + opts['page_size']
            else:
                count = total_records
        return output