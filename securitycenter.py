import httplib
import json
from zipfile import ZipFile
from StringIO import StringIO
from urllib import urlencode


class APIError(Exception):
    def __init__(self, code, msg):
        self.code = code
        self.msg = msg
    def __str__(self):
        return repr('[%s]: %s' % (self.code, self.msg))


class SecurityCenter(object):
    _token = None
    _host = None
    _conn = httplib.HTTPSConnection
    _cookie = None
    _debug = False
    _ver = {
        4.2: '/sc4/request.php',
        4.4: '/request.php',
    }

    def __init__(self, host, user, passwd, login=True, version=4.4, 
                 port=443, debug=False):
        self._host = host
        self._debug = debug
        self._port = port

        # Depricating this as all Security Center installs should be reporting
        # over SSL only anyway.
        #if ssl:
        #    self._conn = httplib.HTTPSConnection
        #else:
        #    self._conn = httplib.HTTPConnection

        self._url = self._ver[version]

        if login:
            self.login(user, passwd)


    def _request(self, module, action, data={}, headers={}, dejson=True):
        # This is the post request that will be sent to the API.  We will expand
        # this as we go along, however we should declare the basics first.
        jdata = {
            'request_id': 1,    # I honestly dont know what this does, however
                                # I have only ever seen it set to 1.  It's never
                                # failed me like this though.
            'module': module,
            'action': action,
            'input': json.dumps(data)
        }

        # If the token is set, then add it into the dictionary so that we can
        # perform this action as the authenticated user.
        if self._token is not None:
            jdata['token'] = self._token

        # Here we are performing the same thing with cookies.  If there are any
        # set, then we should set the cookie header.
        if self._cookie is not None:
            headers['Cookie'] = self._cookie

        # Next we will url encode the payload and then calculate it's length for
        # the Content-Length header.  We might as well set the Content-Type
        # header here as well.
        payload = urlencode(jdata)
        headers['Content-Length'] = len(payload)
        headers['Content-Type'] = 'application/x-www-form-urlencoded'

        # Now it's time to make the connection and actually talk to SC.
        http = self._conn(self._host, self._port)
        http.request('POST', self._url, body=payload, headers=headers)
        resp = http.getresponse()
        data = resp.read()

        # now that we have all of this data, lets go ahead and check to see if
        # Security Center set a cookie.  if it did, then lets set the cookie
        # variable in the object.
        if resp.getheader('set-cookie') is not None:
            self._cookie = resp.getheader('set-cookie')

        # Lastly we need to return the response payload to the calling function
        # in the format that the function wants it.  There are cases where we
        # will not want the payload converted from json, hence why we are
        # handling it this way.
        if dejson:
            return json.loads(data)
        else:
            return data


    def raw_query(self, module, action, data={}, headers={}, dejson=True):
        '''raw_query module, action, [data], [headers], [dejson]
        Initiates a raw query to the api.  While publicly exposed it is not
        recommended to use this function unless there is a legitimate reason
        and a solid understanding of how the API works.
        '''

        # First we query the API and then check to see if an error was thrown.
        # If there was an error, simply respond back with False.
        data = self._request(module, action, data, headers, dejson)
        if dejson:
            if data['error_code']:
                raise APIError(data['error_code'], data['error_msg'])
            return data['response']
        else:
            return data


    def query(self, tool, filters=None, source='cumulative', sort=None,
              direction='desc', func=None, func_params=None, req_size=1000, 
              **filterset):
        '''query tool, [filters], [req_size], [list, of, filters]
        This function attempts to make it a lot easier to run vuln and lce
        searches within the Security Center API.  This function will query the
        API for all of the items that match this query and will then
        return the end result back as a single block.  This means that running
        large queries with this function can consume a large amount of memory
        so some care must be taken.

        If any filters need to be specified that cannot simply be expressed as
        filterName=value then you must fully build that specific filter or list
        of filters.  If this is the case, then you must overload the filters
        value with a list of the filter dictionary sets that are needed.  For
        example:

        [{'filterName': FILTERNAME, 'operator': '=', 'value': VALUE}]

        While we dont expect this to be used much, its there incase it's needed.

        The default request size is also set to 1000.  This means that the
        maximum request size that a singular query can consume is 1000
        individual results before rolling on to the next query.

        If the mitigated flag is set, the results returned back will be from
        the mitigated dataset instead of the cumulative dataset.

        For a list of the available filters that can be performed, please
        consult the Security Center API documentation.
        '''
        data = []       # This is the list that we will be returning back to
                        # the calling function once we complete.
        payload = {}    # The dataset that we will be sending to the API via the
                        # raw_query function.
        # A simple data dictionary to determine the module that we will be used
        stype = {'cumulative': 'vuln', 'mitigated': 'vuln', 'lce': 'events'}


        # Check to see if filters was set.  If it wasnt, then lets go ahead and
        # initialize it as an empty dictionary.
        if filters == None:
            filters = []

        if func_params == None:
            func_params = {}

        # Here is where we expand the filterset dictionary to something that the
        # API can actually understand.
        for item in filterset:
            filters.append({
                'filterName': item,
                'operator': '=',
                'value': filterset[item]
                })

        # Next we need to populate the payload with the information needed to
        # fire a complete API request.
        payload['tool'] = tool
        payload['sourceType'] = source
        payload['filters'] = filters

        # Then we will check to see if a sort field was specified.  If it was,
        # then we will add the sortField and sortDir elements to the query.
        if sort is not None:
            payload['sortField'] = sort
            payload['sortDir'] = direction

        # Now that we have everything we need, a quick sanity check first to
        # make sure some idiot didn't give us a completely empty filterset to
        # work with.  If they did for some reason, just return an empty list.
        #if len(filters) < 1:
        #    return []

        # Everything is set, checks out, and is ready to go.  Now we have to
        # start running through the query loop and actually pull everything
        # together.  We know that we will 
        items = []      # This is the resultset.  It'll be different every time
                        # we loop.  to get things going however, we will just
                        # set it to an empty list.
        count = 0       # A simple counter to track the total number of results
                        # that have been returned.
        while len(items) == req_size or count == 0:
            # The API requires that we set an offset for the start and end of
            # the request, so we will add these to the payload here.
            payload['startOffset'] = count
            payload['endOffset'] = count + req_size

            # Now lets run the query, assign the items, and inc the counter.
            response = self.raw_query(stype[source], 'query', data=payload)
            items = response['results']
            count += len(items)

            # New we will either flatten the data to the data list, or if func
            # is defined, we will pass the data for this query on to that
            # function for parsing.
            if func is not None and hasattr(func, '__call__'):
                func(items, **func_params)
            else:
                for item in items:
                    data.append(item)

            # Lastly lets check to see if we entered into an empty dataset.  If
            # we did, then we will need to break out of the loop so that we
            # don't run into an infinite loop and thrash the API.
            if response['totalRecords'] == '0':
                break
        return data


    def login(self, user, passwd):
        '''login user passwd
        Performs the login operation for Security Center, storing the token
        that Security Center has generated for this login session for future
        queries.
        '''
        data = self._request('auth', 'login',
                             data={'username': user, 'password': passwd})
        self._token = data['response']['token']
        self._user = data


    def logout(self):
        '''logout
        Performs a logout on Security Center to clear the session from the
        session table and then 
        '''
        self._request('auth','logout', data={'token': self._token})
        self._token = None


    def assets(self):
        '''assets
        Returns the needed information to parse through all of the asset
        lists assigned to this user.
        '''
        return self.raw_query('asset', 'init')


    def asset_update(self, asset_id, name=None, description=None,
                     visibility=None, group=None, users=None, 
                     ips=None, rules=None):
        '''asset_update asset_id, [name], [description], [visibility], [group],
                        [users], [ips], [rules]
        The Asset Update function will update the Asset ID defined with the
        values that have been specified.  Only those specified will be updated
        as a query is first made to pre-populate the update with all of the
        existing information, then override that information with the new data
        presented by the caller.
        '''

        payload = None
        # First thing we need to do is query the api for the current asset
        # information and populate the payload with it.
        for asset in self.assets()['assets']:
            if asset['id'] == str(asset_id):
                payload = {
                    'id': asset['id'],
                    'type': asset['type'],
                    'name': asset['name'],
                    'description': asset['description'],
                    'visibility': asset['visibility'],
                    'group': asset['group'],
                    'users': asset['users']
                }
                if asset['type'] == 'dynamic':
                    payload['rules'] = asset['rules']
                if asset['type'] == 'static':
                    payload['definedIPs'] = asset['definedIPs']

        # New we need to check to see if we actually got to pre-load the
        # payload.  If we didnt, then there isn an existing Asset list and we
        # should error out.
        if payload == None:
            raise APIError(1, 'asset_id %s does not exist' % asset_id)

        # And now we will override any of the values that have actually been
        # specified.
        if name is not None and isinstance(name, str):
            payload['name'] = name
        if description is not None and isinstance(description, str):
            payload['description'] = description
        if visibility is not None and isinstance(visibility, str):
            payload['visibility'] = visibility
        if group is not None and isinstance(group, str):
            payload['group'] = group
        if users is not None and isinstance(users, list):
            ulist = []
            for user in users:
                ulist.append({'id': int(user)})
            payload['users'] = ulist
        if payload['type'] == 'dynamic' and rules is not None\
                                        and isinstance(rules, list):
            payload['rules'] = rules
        if payload['type'] == 'static' and ips is not None\
                                       and isinstance(ips, list):
            payload['definedIPs'] = ','.join(ips)

        # And now that we have everything defined, we can go ahead and send
        # the api request payload and return the response.
        return self.raw_query('asset', 'edit', data=payload)


    def asset_ips(self, asset_id):
        '''asset_ips asset_id
        Returns the IPs associated with the asset ID defined.
        '''
        return self.raw_query('asset', 'getIPs', data={'id': asset_id})


    def scan_list(self, start_time=None, end_time=None):
        '''scan_list
        Returns a list of scans stored in Security Center
        '''
        if start_time == None or end_time == None:
            data = self.raw_query('scanResult', 'init')
        else:
            payload = {
                'startTime': int(start_time),
                'endTime': int(end_time),
            }
            data = self.raw_query('scanResult', 'getRange', data=payload)
        return data['scanResults']


    def scan_download(self, scan_id, format='nessus'):
        '''scan_download scan_id [format]
        Will download an individual scan and return a StringIO object with the
        results.

        INCOMPLETE & UNDER ACTIVE DEV
        '''
        payload = {
            'downloadType': format,
            'scanResultID': scan_id,
        }
        data = self.raw_query('scanResult', 'download', data=payload, dejson=False)
        return data
