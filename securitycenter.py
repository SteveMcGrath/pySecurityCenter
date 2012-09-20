import httplib
import datetime
import time
import random
import os
import mimetypes
from zipfile import ZipFile
from StringIO import StringIO
from urllib import urlencode
from poster.encode import multipart_encode

# Here we will attempt to import the simplejson module if it exists, otherwise
# we will fall back to json.  This should solve a lot of issues with python 2.4
# and 3.x.
try:
    import simplejson as json
except ImportError:
    import json


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
    system = None
    _xrefs = ['ICS_ALERT', 'zone_h', 'OSVDB', 'USN', 'NessusID', 'GLSA', 
              'OpenPKG_SA', 'CONNECTIVA', 'AUSCERT', 'MDKSA', 'CERT_FI',
              'MSFT', 'CVE', 'SuSE', 'CERTA', 'BID', 'CISCO_BUG_ID',
              'CISCO_SA', 'RHSA', 'Secunia', 'EDB_ID', 'MSVR', 'TLSA',
              'IAVA', 'CLSA', 'NSFOCUS', 'OWASP', 'CWE', 'DSA', 'HPSB',
              'APPLE_SA', 'CERT_VU', 'CERT', 'TSLSA', 'ICSA', 'VMSA',
              'SSA',
              ]

    def __init__(self, host, user, passwd, login=True, 
                 port=443, debug=False, populate=False):
        self._host = host
        self._debug = debug
        self._port = port
        self._url = '/request.php'

        if login:
            self.system = self._system()
            self.version = self.system['version']
            self.login(user, passwd)
        if populate:
            self._build_xrefs()


    def _revint(self, version):
        # Internal function to convert a version string to an integer.
        intrev = 0
        vsplit = version.split('.')
        for c in range(len(vsplit)):
            item = int(vsplit[c]) * (10 ** (((len(vsplit) - c - 1)* 2)))
            intrev += item
        return intrev


    def _revcheck(self, func, version):
        # Internal function to see if a version is func than what we have
        # determined to be talking to.  This is very useful for newer API calls
        # to make sure we don't accidentally make a call to something that
        # doesnt exist.
        current = self._revint(self.version)
        check = self._revint(version)
        if func in ('lt', '<=',): return check <= current
        elif func in ('gt', '>='): return check >= current
        elif func in ('eq', '=', 'equals'): return check == current
        else: return False


    def _build_xrefs(self):
        # Internal function to populate the xrefs list with the external
        # references to be used in searching plugins and potentially
        # other functions as well.
        xrefs = set()

        plugins = self.plugins()
        for plugin in plugins:
            for xref in plugin['xrefs'].split(', '):
                xrf = xref.replace('-', '_').split(':')[0]
                if xrf is not '':
                    xrefs.add(xrf)
        self._xrefs = list(xrefs)


    def _gen_multipart(self, jdata, filename):
        # This is an internal function to be able to upload files to Security
        # Center.  Based on the awsome work done with the recipe linked below:
        # http://code.activestate.com/recipes/146306/
        boundry = '----------MultiPartWebFormBoundry'
        data = []
        for item in jdata:
            data.append('--' + boundry)
            data.append('Content-Disposition: form-data; name="%s"' % item)
            data.append('')
            data.append(str(jdata[item]))
        data.append('--' + boundry)
        data.append(
            'Content-Disposition: form-data; name="%s"; filename="%s"' %\
            ('Filedata', os.path.split(filename)[1]))
        data.append('Content-Type: %s' %\
            (mimetypes.guess_type(filename)[0] or 'application/octet-stream'))
        data.append('')
        data.append(open(filename, 'rb').read())
        data.append('--' + boundry + '--')
        data.append('')
        payload = '\r\n'.join(data)
        content_type = 'multipart/form-data; boundary=%s' % boundry
        return content_type, payload


    def _request(self, module, action, data={}, headers={}, dejson=True,
                 filename=False):
        # This is the post request that will be sent to the API.  We will expand
        # this as we go along, however we should declare the basics first.
        jdata = {
            'request_id': random.randint(10000,20000),
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

        if filename:
            # If a filename is specified then we will need to build a multipipart
            # object.
            content_type, payload = self._gen_multipart(jdata, filename)
            headers['Content-Type'] = content_type
        else:
            # Here we will url encode the payload and then calculate it's length for
            # the Content-Length header.  We might as well set the Content-Type
            # header here as well.
            payload = urlencode(jdata)
            headers['Content-Type'] = 'application/x-www-form-urlencoded'
        headers['Content-Length'] = len(payload)

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


    def raw_query(self, module, action, data={}, headers={}, dejson=True,
                  filename=None):
        '''raw_query module, action, [data], [headers], [dejson]
        Initiates a raw query to the api.  While publicly exposed it is not
        recommended to use this function unless there is a legitimate reason
        and a solid understanding of how the API works.
        '''

        # First we query the API and then check to see if an error was thrown.
        # If there was an error, simply respond back with False.
        data = self._request(module, action, data, headers, dejson, filename)
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
                if func_params is not None:
                    func(items, **func_params)
                else:
                    func(items)
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
            raise APIError(13, 'asset_id %s does not exist' % asset_id)

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
            for user in users:                ulist.append({'id': int(user)})
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


    def credentials(self):
        '''credentials
        Returns the list of credentials that the user has access to.
        '''
        return self.raw_query('credential', 'init')


    def credential_update(self, cred_id, **options):
        '''credential_update cred_id **options
        Updates the specified values of the credential ID specified.
        '''
        payload = None

        # First we pull the credentials and populate the payload if we
        # find a match.
        for cred in self.credentials()['credentials']:
            if cred['id'] == str(cred_id):
                payload = {
                    'id': cred_id,
                    'type': cred['type'],
                    'name': cred['name'],
                    'description': cred['description'],
                    'visibility': cred['visibility'],
                    'group': cred['group'],
                    'users': cred['users'],
                }

                if cred['type'] == 'kerberos':
                    payload['ip'] = cred['ip']
                    payload['port'] = cred['port']
                    payload['protocol'] = cred['protocol']
                    payload['realm'] = cred['realm']

                if cred['type'] == 'snmp':
                    payload['communityString'] = cred['communityString']

                if cred['type'] == 'ssh':
                    payload['username'] = cred['username']
                    payload['publickey'] = cred['publickey']
                    payload['privatekey'] = cred['privatekey']
                    payload['priviledgeEscalation'] = cred['priviledgeEscalation']
                    payload['escalationUsername'] = cred['escalationUsername']

                if cred['type'] == 'windows':
                    payload['username'] = cred['username']
                    payload['domain'] = cred['domain']

        if payload == None:
            raise APIError(13, 'cred_id %s does not exist' % cred_id)

        for option in options:
            payload[option] = options[option]

        return self.raw_query('credential', 'edit', data=payload)


    def plugins(self, plugin_type='all', sort='id', direction='asc',
                size=1000, all=True, loops=0, since=None, **filterset):
        '''plugins
        Returns a list of of the plugins and their associated families.  For
        simplicity purposes, the plugin family names will be injected into the
        plugin data so that only 1 list is returned back with all of the
        information.
        '''
        plugins = []

        # First we need to generate the basic payload that we will be augmenting
        # to build the 
        payload = {
            'size': size,
            'offset': 0,
            'type': plugin_type,
            'sortField': sort,
            'sortDirection': direction.upper(),
        }

        # If there was a filter given, we will need to populate that.
        if len(filterset) > 0:
            fname = filterset.keys()[0]
            if fname in self._xrefs:
                fname = 'xrefs:%s' % fname.replace('_','-')
            payload['filterField'] = fname
            payload['filterString'] = filterset[filterset.keys()[0]]

        # We also need to check if there was a datetime object sent to us and
        # parse that down if given.
        if since is not None and (isinstance(since, datetime.datetime) or
                                  isinstance(since, datetime.date)):
            payload['since'] = int(time.mktime(since.timetuple()))

        # And now we run through the loop needed to pull all of the data.  This
        # may take some time even though we are pulling large data sets.  At the
        # time of development of this module, there were over 55k active plugins
        # and over 7k passive ones.
        while all or loops > 0:
            # First things first, we need to query the data.
            data = self.raw_query('plugin', 'init', data=payload)
            if data == []:
                return []

            # This no longer works in 4.4 as the family name is already
            # referenced.  Will re-activate this code when I can get a SC4.2
            # Instance up and running to test...
            # ---
            # Next we convert the family dictionary list into a flat dictionary.
            #fams = {}
            #for famitem in data['families']:
            #    fams[famitem['id']] = famitem['name']

            # Then we parse thtrough the data set, adding in the family name
            # into the plugin definition before adding it into the plugins list.
            for plugin in data['plugins']:
            #    plugin['familyName'] = fams[plugin['familyID']]
                plugins.append(plugin)
            # ---

            # Next its time to increment the offset so that we get a new data
            # set.  We will also check here to see if the length really is the
            # same as whats specified in the size variable.  If it isnt, then 
            # we have reached the end of the dataset and might as well set 
            # the continue variable to False.
            if len(data['plugins']) < size:
                all = False
                loops = 0
            else:
                loops -= 1
                payload['offset'] += len(data['plugins'])
        return plugins


    def plugin_counts(self):
        '''plugin_counts
        Returns the plugin counts as dictionary with the last updated info if
        its available.
        '''
        ret = {
            'total': 0,
        }

        # As ususal, we need data before we can actually do anything ;)
        data = self.raw_query('plugin', 'init')

        # For backwards compatability purposes, we will be handling this a bit
        # differently than I would like.  We are going to check to see if each
        # value exists and override the default value of 0.  The only value that
        # I know existed in bost 4.2 and 4.4 is pluginCount, the rest aren't
        # listed in the API docs, however return back from my experimentation.
        ret['total'] = data['pluginCount']

        if 'lastUpdates' in data:
            for item in ['active', 'passive', 'compliance', 'custom']:
                itemdata = {}
                if item in data['lastUpdates']:
                    itemdata = data['lastUpdates'][item]
                if item in data:
                    itemdata['count'] = data[item]
                else:
                    itemdata['count'] = 0

                ret[item] = itemdata
        return ret


    def plugin_details(self, plugin_id):
        '''plugin_details plugin_id
        Returns the details for a specific plugin id
        '''
        return self.raw_query('plugin', 'getDetails', 
                              data={'pluginID': plugin_id})


    def repositories(self):
        '''repositories
        Returns with the repository information. license information, and
        organizational information.
        '''
        return self.raw_query('repository', 'init')


    def roles(self):
        '''roles
        Returns the user roles and associated metadata.
        '''
        return self.raw_query('role', 'init')


    def _system(self):
        '''system
        Returns system information about the Security Center instance.
        '''
        return self.raw_query('system', 'init')


    def tickets(self):
        '''tickets
        Returns tickets and their asociated data
        '''
        return self.raw_query('ticket', 'init')

    def users(self):
        '''users
        Returns all user information from the Security Center instance.
        '''
        return self.raw_query('user', 'init')


    def vulns(self):
        '''vulns
        Returns all available vulnerabilities from the Security Center instance.
        '''
        return self.raw_query('vuln', 'init')


    def ip_info(self, ip, repository_ids=[]):
        '''ip_info
        Returns information about the IP specified in the repository ids
        defined.
        '''
        repos = []
        for rid in repository_ids:
            repos.append({'id': rid})
        return self.raw_query('vuln', 'getIP', data={
            'ip': ip, 'repositories': repos})


    def zones(self):
        '''zones
        Returns all available scan zones and scanner status information.
        '''
        return self.raw_query('zone', 'init')


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


    def scan_download(self, scan_id, format='v2'):
        '''scan_download scan_id [format]
        Will download an individual scan and return a string with the results.
        '''
        payload = {
            'downloadType': format,
            'scanResultID': scan_id,
        }
        data = self.raw_query('scanResult', 'download', data=payload, dejson=False)
        bobj = StringIO()
        bobj.write(data)
        zfile = ZipFile(bobj)
        return zfile.read(zfile.namelist()[0])


    ### WARNING ###
    # All of the functions below are not part of the API documentation.  This
    # means that it is entirely possible for one or all of these to change
    # without notification as they are not part of the documented API.
    ###############

    def _upload(self, filename):
        '''_upload filename
        Internal function to provide uploading capability.  All of the heavy
        Lifting work has been handled upstream in self._request.

        UN-DOCUMENTED CALL: This function is not considered stable.
        '''
        return self.raw_query('file', 'upload', data={'returnContent':'false'},
                              filename=filename)


    def dashboard_import(self, name, filename):
        '''dashboard_import Dashboard_Name, filename
        Uploads a dashboard template to the current user's dashboard tabs.

        UN-DOCUMENTED CALL: This function is not considered stable.
        '''
        data = self._upload(filename)
        return self.raw_query('dashboard', 'importTab', data={
            'filename': data['filename'],
            'name': name,
        })


    def report_import(self, name, filename):
        '''report_import Report_Name, filename
        Uploads a report template to the current user's reports

        UN-DOCUMENTED CALL: This function is not considered stable.
        '''
        data = self._upload(filename)
        return self.raw_query('report', 'import', data={
            'filename': data['filename'],
            'name': name,
        })
