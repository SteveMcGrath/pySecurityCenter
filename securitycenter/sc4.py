########################### LEGACY CODE ###################################
# This code will eventually be phased out.  Once Tenable stops supporting #
# SecurityCenter 4, the 4.x API code will be depricated out.              #
###########################################################################
import calendar
from datetime import date, datetime, timedelta
import httplib
import logging
import mimetypes
import os
import ssl
import random
from StringIO import StringIO
from urllib import urlencode
import urllib2
from urllib2 import urlopen, Request
from zipfile import ZipFile

# Here we will attempt to import the simplejson module if it exists, otherwise
# we will fall back to json.  This should solve a lot of issues with python 2.4
# and 3.x.
try:
    import simplejson as json
except ImportError:
    import json

# Test for SSL support.  Sets a flag has_ssl and defines an HTTPSHandler that
# provides two-way SSL.
# http://stackoverflow.com/a/5707951/400617
try:
    import ssl

    class HTTPSClientAuthHandler(urllib2.HTTPSHandler):
        def __init__(self, key, cert):
            urllib2.HTTPSHandler.__init__(self)
            self.key = key
            self.cert = cert

        def https_open(self, req):
            return self.do_open(self.getConnection, req)

        def getConnection(self, host, **kwargs):
            return httplib.HTTPSConnection(host, key_file=self.key,
                                           cert_file=self.cert, **kwargs)
except ImportError:
    ssl = None


class SecurityCenter4(object):
    '''
    Connects to the SecurityCenter API based on the parameters specified.

    :param host: Address of the SecurityCenter instance.  
                 Can be IP or Hostname.
    :param user: Account name for SecurityCenter
    :param passwd: Account password for SecurityCenter
    :param port: What port to talk to SecurityCenter on (Default is 443)
    :param login: Automatically login to SecurityCenter (Default is True)
    :param key:
    :param cert:
    :param debug: Should SecurityCenter output all calls to a debug log?
                  (Default is False)
    :param populate: Should the module repopulate the _xrefs list?  
                     (Default is False)

    :type host: string
    :type user: string
    :type passwd: string
    :type port: int
    :type login: bool
    :type debug: bool
    :type populate: bool
    '''
    _token = None
    _host = None
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

    def __init__(self, host, user, passwd, login=True, port=443, key=None,
                 cert=None, debug=False, populate=False):
        self._host = host
        self._debug = debug
        self._port = port
        self._url = 'https://%s/request.php' % self._host

        # Build and install an HTTPS opener if SSL support is available
        if ssl is not None and None not in (key, cert):
            cert_handler = HTTPSClientAuthHandler(key, cert)
            opener = urllib2.build_opener(cert_handler)
            urllib2.install_opener(opener)

        # Debugging Log Settings...
        self._log = logging.getLogger('pySecurityCenter')
        if debug:
            handler = logging.FileHandler('pySecurityCenter-DEBUG.log')
            formatter = logging.Formatter('%(asctime)s %(message)s')
            handler.setFormatter(formatter)
            self._log.setLevel(logging.DEBUG)
            self._log.addHandler(handler)

        if login:
            self.system = self._system()
            self.version = self.system['version']
            self.login(user, passwd)
        if populate:
            self._build_xrefs()

    def _revint(self, version):
        '''
        Internal function to convert a version string to an integer.
        '''
        intrev = 0
        vsplit = version.split('.')
        for c in range(len(vsplit)):
            item = int(vsplit[c]) * (10 ** (((len(vsplit) - c - 1) * 2)))
            intrev += item
        return intrev

    def _revcheck(self, func, version):
        '''
        Internal function to see if a version is func than what we have
        determined to be talking to.  This is very useful for newer API calls
        to make sure we don't accidentally make a call to something that
        doesnt exist.
        '''
        current = self._revint(self.version)
        check = self._revint(version)
        if func in ('lt', '<=',):
            return check <= current
        elif func in ('gt', '>='):
            return check >= current
        elif func in ('eq', '=', 'equals'):
            return check == current
        else:
            return False

    def _build_xrefs(self):
        '''
        Internal function to populate the xrefs list with the external
        references to be used in searching plugins and potentially
        other functions as well.
        '''
        xrefs = set()

        plugins = self.plugins()
        for plugin in plugins:
            for xref in plugin['xrefs'].split(', '):
                xrf = xref.replace('-', '_').split(':')[0]
                if xrf is not '':
                    xrefs.add(xrf)
        self._xrefs = list(xrefs)

    def _gen_multipart(self, jdata, filename):
        '''
        This is an internal function to be able to upload files to Security
        Center.  Based on the awsome work done with the recipe linked below:
        http://code.activestate.com/recipes/146306/
        '''

        # As we will be accepting both filenames, or file objects 
        # (because why not!) we will need to make a few determinations on what
        # we are doing beforehand.
        if isinstance(filename, file) or isinstance(filename, StringIO.StringIO):
            
            # If we are parsing a file object, then we should try to pull as
            # much information about the file object that was passed as we can,
            # however we do need to be able to fall back to some generic info
            # incase we get based a StringIO object as StringIO has no
            # associated filename.
            content = filename.read()
            try:
                data_name = filename.name
                content_header = 'Content-Type: %s' %\
                             (mimetypes.guess_type(data_name)[0] or
                              'application/octet-stream')
            except:
                content_header = 'Content-Type: application/octet-stream'
                data_name = 'pyobj-%s' % random.randint(20000)
        else:

            # It appears that we got passed a string object with a filename, so
            # we will go ahead and parse it as such.
            data_name = os.path.split(filename)[1]
            content_header = 'Content-Type: %s' %\
                             (mimetypes.guess_type(data_name)[0] or
                              'application/octet-stream')
            content = open(filename, 'rb').read()

        boundry = '----------MultiPartWebFormBoundry'
        data = []
        for item in jdata:
            data.append('--' + boundry)
            data.append('Content-Disposition: form-data; name="%s"' % item)
            data.append('')
            data.append(str(jdata[item]))
        data.append('--' + boundry)
        data.append(
            'Content-Disposition: form-data; name="%s"; filename="%s"' %
            ('Filedata', data_name))
        data.append(content_header)
        data.append('')
        data.append(content)
        data.append('--' + boundry + '--')
        data.append('')
        payload = '\r\n'.join(data)
        content_type = 'multipart/form-data; boundary=%s' % boundry
        return content_type, payload

    def _request(self, module, action, data=None, headers=None, dejson=True,
                 filename=False):
        '''
        This is the core internal function for interacting with the API.  All 
        calls to the API get routed through here.

        :param module: The API module being called (Refer to SecurityCenter API 
                       Documentation). 
        
        :param action: The API action being called (Refer to SecurityCenter API
                       Documentation). 
        
        :param data: A dictionary of the data to send to the API (default None)
        :param headers: A dictional of additional headers to send to the API 
                        (default None).

        :param dejson: Should the module convert the JSON response back to a
                       python dictionary (default is True).

        :param filename: A string filename or file object to be passed to the 
                         API.  The default is to send nothing.

        :type module: string
        :type action: string
        :type data: dict
        :type headers: dict 
        :type dejson: bool
        :type filename: string, fileobj
        '''

        # This is the post request that will be sent to the API.  We will expand
        # this as we go along, however we should declare the basics first.
        if not data:
            data = {}
        if not headers:
            headers = {}

        jdata = {
            'request_id': random.randint(10000, 20000),
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

        # For a little logging action, lets post everything we have to the log.
        self._log.debug('\n'.join([
            'POST SEND DATA TO %s' % self._host,
            'HEADERS:',
            '\n'.join(['\t%-30s: %s' % (a, headers[a]) for a in headers]),
            'DATA:',
            payload,
            '\n',
        ]))

        # Now it's time to make the connection and actually talk to SC.
        resp = urlopen(Request(self._url, payload, headers), context=ssl.SSLContext(ssl.PROTOCOL_TLSv1))
        data = resp.read()

        # And we need to log the response as well....
        self._log.debug('\n'.join([
            'API RESPONSE DATA FROM %s' % self._host,
            'HEADERS:',
            '\n'.join([a for a in resp.headers.headers]),
            'DATA:',
            data,
            '\n',
        ]))

        # now that we have all of this data, lets go ahead and check to see if
        # Security Center set a cookie.  if it did, then lets set the cookie
        # variable in the object.
        if resp.headers.getheader('set-cookie') is not None:
            self._cookie = resp.headers.getheader('set-cookie')

        # Lastly we need to return the response payload to the calling function
        # in the format that the function wants it.  There are cases where we
        # will not want the payload converted from json, hence why we are
        # handling it this way.
        if dejson:
            return json.loads(data)
        else:
            return data

    def raw_query(self, module, action, data=None, headers=None, dejson=True,
                  filename=None):
        """raw_query module, action, [data], [headers], [dejson]
        Initiates a raw query to the api.  While publicly exposed it is not
        recommended to use this function unless there is a legitimate reason
        and a solid understanding of how the API works.
        """
        if not data:
            data = {}
        if not headers:
            headers = {}

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
              scan=None, directory=None, **filterset):
        """query tool, [filters], [req_size], [list, of, filters]
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

        If the source is `"individual"`, `scan` should be passed a scan id and
        `directory` should be passed a date directory as a string `"YYYY-mm-dd"`
        or as a `datetime` to be converted.

        For a list of the available filters that can be performed, please
        consult the Security Center API documentation.

        """

        data = []       # This is the list that we will be returning back to
                        # the calling function once we complete.
        payload = {}    # The dataset that we will be sending to the API via the
                        # raw_query function.

        # A simple data dictionary to determine the module that we will be used
        stype = {
            'cumulative': 'vuln',
            'mitigated': 'vuln',
            'patched': 'vuln',
            'individual': 'vuln',
            'lce': 'events',
        }

        # When the source is "individual", scan and directory should be provided
        # as well, and will be set in the payload.
        if source == "individual" and scan is not None and directory is not None:
            # convert directory passed as datetime to string if necessary
            if isinstance(directory, date):
                directory = directory.strftime("%Y-%m-%d")

            payload["scanID"] = scan
            payload["dateDirectory"] = directory
            payload["view"] = "all"

        # Check to see if filters was set.  If it wasnt, then lets go ahead and
        # initialize it as an empty dictionary.
        if filters is None:
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
        """login user passwd
        Performs the login operation for Security Center, storing the token
        that Security Center has generated for this login session for future
        queries.
        """
        data = self._request('auth', 'login',
                             data={'username': user, 'password': passwd})

        if data["error_code"]:
            raise APIError(data["error_code"], data["error_msg"])

        self._token = data["response"]["token"]
        self._user = data

    def logout(self):
        """logout
        Performs a logout on Security Center to clear the session from the
        session table and then
        """
        self._request('auth', 'logout', data={'token': self._token})
        self._token = None

    def assets(self):
        """assets
        Returns the needed information to parse through all of the asset
        lists assigned to this user.
        """
        return self.raw_query('asset', 'init')

    def asset_update(self, asset_id, name=None, description=None,
                     visibility=None, group=None, users=None,
                     ips=None, rules=None, dns=None):
        '''asset_update asset_id, [name], [description], [visibility], [group],
                        [users], [ips], [rules], [dns]
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
                }
                if self.version[:3] == '4.8':
                    payload['tags'] = asset['tags']
                else:
                    payload['visibility'] = asset['visibility']
                    payload['group'] = asset['group']
                    payload['users'] = asset['users']
                if asset['type'] == 'dynamic':
                    payload['rules'] = asset['rules']
                if asset['type'] == 'static':
                    payload['definedIPs'] = asset['definedIPs']
                if asset['type'] == 'dnsname':
                    payload['definedDNSNames'] = asset['definedDNSNames']


        # New we need to check to see if we actually got to pre-load the
        # payload.  If we didnt, then there isn an existing Asset list and we
        # should error out.
        if payload is None:
            raise APIError(13, 'asset_id %s does not exist' % asset_id)

        # And now we will override any of the values that have actually been
        # specified.
        if name is not None and isinstance(name, str):
            payload['name'] = name
        if description is not None and isinstance(description, str):
            payload['description'] = description
        if self.version[:3] != '4.8':
            if visibility is not None and isinstance(visibility, str):
                payload['visibility'] = visibility
            if group is not None and isinstance(group, str):
                payload['group'] = group
        else:
            if group is not None and isinstance(group, str):
                payload['tags'] = group
        if users is not None and isinstance(users, list):
            ulist = []
            for user in users:
                ulist.append({'id': int(user)})
            payload['users'] = ulist
        if payload['type'] == 'dynamic' and rules is not None and isinstance(rules, list):
            payload['rules'] = rules
        if payload['type'] == 'static' and ips is not None and isinstance(ips, list):
            payload['definedIPs'] = ','.join(ips)
        if payload['type'] == 'dnsname' and dns is not None\
                                        and isinstance(dns, list):
            payload['definedDNSNames'] = ','.join(dns)

        # And now that we have everything defined, we can go ahead and send
        # the api request payload and return the response.
        return self.raw_query('asset', 'edit', data=payload)

    def asset_ips(self, asset_id):
        """asset_ips asset_id
        Returns the IPs associated with the asset ID defined.
        """
        return self.raw_query('asset', 'getIPs', data={'id': asset_id})

    def credentials(self):
        """credentials
        Returns the list of credentials that the user has access to.
        """
        return self.raw_query('credential', 'init')

    def credential_update(self, cred_id, **options):
        """credential_update cred_id **options
        Updates the specified values of the credential ID specified.
        """
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

        if payload is None:
            raise APIError(13, 'cred_id %s does not exist' % cred_id)

        for option in options:
            payload[option] = options[option]

        return self.raw_query('credential', 'edit', data=payload)

    def credential_add(self, name, cred_type, **options):
        '''
        Adds a new credential into SecurityCenter.  As credentials can be of
        multiple types, we have different options to specify for each type of
        credential.

        **Global Options (Required)**

        :param name: Unique name to be associated to this credential
        :param cred_type: The type of credential.  Valid values are:
                          'ssh', 'windows', 'snmp', or 'kerberos'
        :type name: string
        :type cred_type: string

        **Windows Credential Options**

        :param username: Account Name
        :param password: Account Password 
        :param domain: [Optional] Account Member Domain
        :type username: string
        :type password: string
        :type domain: string

        **Unix/SSH Credential Options**

        SSH Credentials cover a multitude of different types of hosts. 
        Everything from Linux/Unix boxes to networking gear like Cisco IOS
        devices.  As a result of this, there are a lot of available options in
        order to cover as many possible scenarios as possible.  A few examples:

        Simple Username/Password:

        >>> sc.credential_add('Example Linux Root', 'ssh', 
                username='root', password='r00tp@ssw0rd')
        
        Utilizing Sudo:

        >>> sc.credential_add('Example Linux Sudo', 'ssh',
                username='user', password='p@ssw0rd',
                privilegeEscalation='sudo',
                escalationPassword='p@ssw0rd')

        SSH Keys (By Filename):

        >>> sc.credential_add('Example Linux Keys', 'ssh',
                username='root',
                privateKey='/path/to/id_rsa',
                publicKey='/path/to/id_rsa.pub',
                passphrase='somthing' # Only use this if needed
            )

        SSH Keys (Using File Objects):

        >>> pubkey = open('/path/to/id_rsa.pub', 'rb')
        >>> privkey = open('/path/to/id_rsa', 'rb')
        >>> sc.credential_add('Example Linux Keys 2', 'ssh',
                username='root',
                privateKey=privkey,
                publicKey=pubkey,
                passphrase='somthing' # Only use this if needed
            )

        :param username: Account Name
        :param password: Account Password
        :param privilegeEscalation: [Optional] The type of privilege escalation 
                                required for this account.  The default is None.
                                Valid options are: 'su', 'su+sudo', 'dzdo', 
                                'pbrun', 'Cisco \'enable\'', or 'none'.
        :param escalationUsername: [Optional] The username to escalate to.  Only
                                   used for su+sudo escalation. 
        :param escalationPassword: [Optional] The password used for escalation.
        :param publicKey: [Optional] The SSH public RSA/DSA key used for
                          authentication.
        :param privateKey: [Optional] The SSH private RSA/DSA key used for 
                           authentication. 
        :param passphrase: [Optional] The passphrase needed for the RSA/DSA
                           keypair.
        :type username: string
        :type password: string
        :type privilegeEscalation: string
        :type escalationUsername: string
        :type escalationPassword: string
        :type publicKey: string [filename], fileobj
        :type privateKey: string [filename], fileobj
        :type passphrase: string

        **Kerberos Credential Options**

        :param ip: Kerberos Host IP
        :param port: Kerberos Host Port
        :param realm: Kerberos Realm
        :param protocol: Kerberos Protocol
        :type ip: string
        :type port: string
        :type realm: string
        :type protocol: string

        **SNMP Community String**

        :param communityString: The community string to connect with. 
        :type communityString: string
        '''

        if 'pirvateKey' in options:
            options['privateKey'] = self._upload(options['privateKey'])['filename']
        if 'publicKey' in options:
            options['publicKey'] = self._upload(options['publicKey'])['filename']

        return self.raw_query("credential", "add", data=options)

    def credential_share_simulate(self, cred_id, *user_ids):
        """Shares a given credential to the specified Users. 
        
        :param cred_id: Credential ID
        :param user_ids: List of User IDs 
        """
        return self.raw_query("credential", "shareSimulate", data={
            'id': cred_id,
            'users': [{'id': i} for i in user_ids],
        })

    def credential_share(self, cred_id, *user_ids):
        """Shares a given credential to the specified Users. 
        
        :param cred_id: Credential ID
        :param user_ids: List of User IDs 
        """
        return self.raw_query("credential", "share", data={
            'id': cred_id,
            'users': [{'id': i} for i in user_ids],
        })

    def credential_delete_simulate(self, *ids):
        """Show the relationships and dependencies for one or more credentials.

        :param ids: one or more credential ids
        """
        return self.raw_query("credential", "deleteSimulate", data={
            "credentials": [{"id": str(id)} for id in ids]
        })

    def credential_delete(self, *ids):
        """Delete one or more credentials.

        :param ids: one or more credential ids
        """
        return self.raw_query("credential", "delete", data={
            "credentials": [{"id": str(id)} for id in ids]
        })

    def plugins(self, plugin_type='all', sort='id', direction='asc',
                size=1000, offset=0, all=True, loops=0, since=None, **filterset):
        """plugins
        Returns a list of of the plugins and their associated families.  For
        simplicity purposes, the plugin family names will be injected into the
        plugin data so that only 1 list is returned back with all of the
        information.
        """
        plugins = []

        # First we need to generate the basic payload that we will be augmenting
        # to build the
        payload = {
            'size': size,
            'offset': offset,
            'type': plugin_type,
            'sortField': sort,
            'sortDirection': direction.upper(),
        }

        # If there was a filter given, we will need to populate that.
        if len(filterset) > 0:
            fname = filterset.keys()[0]
            if fname in self._xrefs:
                fname = 'xrefs:%s' % fname.replace('_', '-')
            payload['filterField'] = fname
            payload['filterString'] = filterset[filterset.keys()[0]]

        # We also need to check if there was a datetime object sent to us and
        # parse that down if given.
        if since is not None and isinstance(since, date):
            payload['since'] = calendar.timegm(since.utctimetuple())

        # And now we run through the loop needed to pull all of the data.  This
        # may take some time even though we are pulling large data sets.  At the
        # time of development of this module, there were over 55k active plugins
        # and over 7k passive ones.
        while all or loops > 0:
            # First things first, we need to query the data.
            data = self.raw_query('plugin', 'init', data=payload)
            if not data:
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
        """plugin_counts
        Returns the plugin counts as dictionary with the last updated info if
        its available.
        """
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
            for item in ['active', 'passive', 'compliance', 'custom', 'event']:
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
        """plugin_details plugin_id
        Returns the details for a specific plugin id
        """
        return self.raw_query('plugin', 'getDetails',
                              data={'pluginID': plugin_id})

    def repositories(self):
        """repositories
        Returns with the repository information. license information, and
        organizational information.
        """
        return self.raw_query('repository', 'init')

    def roles(self):
        """roles
        Returns the user roles and associated metadata.
        """
        return self.raw_query('role', 'init')

    def _system(self):
        """system
        Returns system information about the Security Center instance.
        """
        return self.raw_query('system', 'init')

    def tickets(self):
        """tickets
        Returns tickets and their asociated data
        """
        return self.raw_query('ticket', 'init')

    def users(self):
        """users
        Returns all user information from the Security Center instance.
        """
        return self.raw_query('user', 'init')

    def vulns(self):
        """vulns
        Returns all available vulnerabilities from the Security Center instance.
        """
        return self.raw_query('vuln', 'init')

    def ip_info(self, ip, repository_ids=None):
        """ip_info
        Returns information about the IP specified in the repository ids
        defined.
        """
        if not repository_ids:
            repository_ids = []
        repos = []
        for rid in repository_ids:
            repos.append({'id': rid})
        return self.raw_query('vuln', 'getIP', data={
            'ip': ip, 'repositories': repos})

    def zones(self):
        """zones
        Returns all available scan zones and scanner status information.
        """
        return self.raw_query('zone', 'init')

    def scan_list(self, start_time=None, end_time=None, **kwargs):
        """List scans stored in Security Center in a given time range.

        Time is given in UNIX timestamps, assumed to be UTC. If a `datetime` is
        passed it is converted. If `end_time` is not specified it is NOW. If
        `start_time` is not specified it is 30 days previous from `end_time`.

        :param start_time: start of range to filter
        :type start_time: date, datetime, int
        :param end_time: end of range to filter
        :type start_time: date, datetime, int

        :return: list of dictionaries representing scans

        """

        try:
            end_time = datetime.utcfromtimestamp(int(end_time))
        except TypeError:
            if end_time is None:
                end_time = datetime.utcnow()

        try:
            start_time = datetime.utcfromtimestamp(int(start_time))
        except TypeError:
            if start_time is None:
                start_time = end_time - timedelta(days=30)

        data = {"startTime": calendar.timegm(start_time.utctimetuple()),
                "endTime": calendar.timegm(end_time.utctimetuple())}
        data.update(kwargs)

        result = self.raw_query("scanResult", "getRange", data=data)
        return result["scanResults"]

    def scan_download(self, scan_id, format='v2'):
        """scan_download scan_id [format]
        Will download an individual scan and return a string with the results.
        """
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
        """_upload filename
        Internal function to provide uploading capability.  All of the heavy
        Lifting work has been handled upstream in self._request.

        UN-DOCUMENTED CALL: This function is not considered stable.
        """
        return self.raw_query('file', 'upload', data={'returnContent': 'false'},
                              filename=filename)

    def dashboard_import(self, name, filename):
        """dashboard_import Dashboard_Name, filename
        Uploads a dashboard template to the current user's dashboard tabs.

        UN-DOCUMENTED CALL: This function is not considered stable.
        """
        data = self._upload(filename)
        return self.raw_query('dashboard', 'importTab', data={
            'filename': data['filename'],
            'name': name,
        })

    def report_import(self, name, filename):
        """report_import Report_Name, filename
        Uploads a report template to the current user's reports

        UN-DOCUMENTED CALL: This function is not considered stable.
        """
        data = self._upload(filename)
        return self.raw_query('report', 'import', data={
            'filename': data['filename'],
            'name': name,
        })


    def download_repository(self, repo_id):
        '''download_repository Repository_Id
        Download the tarball of the repository id specified.

        UN-DOCUMENTED CALL: This function is not considered stable.
        '''
        return self.raw_query('repository', 'export', data={
            'id': repo_id
        }, dejson=False)


    def asset_create(self, name, items, tag='', description='', atype='static'):
        '''asset_create_static name, ips, tags, description
        Create a new asset list with the defined information.

        UN-DOCUMENTED CALL: This function is not considered stable.

        :param name: asset list name (must be unique)
        :type name: string
        :param items: list of IP Addresses, CIDR, and Network Ranges
        :type items: list
        :param tag: The tag associate to the asset list
        :type tag: string
        :param description: The Asset List description
        :type description: string
        '''
        data = {
            'name': name,
            'description': description,
            'type': atype,
            'tags': tag
        }
        if atype == 'static':
            data['definedIPs'] = ','.join(items)
        if atype == 'dns':
            data['type'] = 'dnsname'
            data['definedDNSNames'] = ' '.join(items)
        return self.raw_query('asset', 'add', data=data)


    def asset_create_combo(self, name, combo, tag='', description=''):
        '''asset_create_combo name, combination, tag, description
        Creates a new combination asset list.  Operands can be either asset list
        IDs or be a nested combination asset list.

        UN-DOCUMENTED CALL: This function is not considered stable.

        AND = intersection
        OR = union
        operand = asset list ID or nested combination.
        operator = intersection or union.

        Example:

        combo = {
            'operand1': {
                'operand1': '2',
                'operand2': '2',
                'operation': 'union',
            },
            'operand2': '3',
            'operation': 'intersection'
        }


        :param name: Name of the asset list.
        :type name: string
        :param combo: dict
        :param tag: The tag of the asset list.
        :type tag: string
        :param description: Description of the asset list.
        :type description: string
        '''
        return self.raw_query('asset', 'add', data={
            'name': name,
            'description': description,
            'type': 'combination',
            'combinations': combo,
        })


    def risk_rule(self, rule_type, rule_value, port, proto, plugin_id, 
                  repo_ids, comment='', expires='-1', severity=None):
        '''accept_risk rule_type, rule_value, port, proto, plugin_id, comment
        Creates an accept rick rule based on information provided.

        UN-DOCUMENTED CALL: This function is not considered stable.

        :param rule_type: Valid options: ip, asset, all.
        :type rule_type: string
        :param rule_value: IP Addresses, or assetID if not the type is not all.
        :type tule_value: string
        :param port: Port number
        :type port: string
        :param proto: Either the protocol ID or any. TCP = 6, UDP = 17, ICMP = 1
        :type proto: string
        :param plugin_id: The plugin ID
        :type plugin_id: string
        :param repo_ids: List of repository ids that the rule pertains to.
        :type repo_ids: string
        :param comment: General purpose comment field.
        :type comment: string
        :param expires: epoch time for expiration.
        :type expires: string
        :param severity: New severity rating.
        '''
        data = {
            'hostType': rule_type,
            'port': port,
            'comments': comments,
            'protocol': proto,
            'pluginID': plugin_id,
            'repIDs': [{'id': i} for i in repo_ids]
        }
        if rule_type != 'all':
            data['hostValue'] = rule_value
        if severity is None:
            data['expires'] = expires
            return self.raw_query('acceptRiskRule', 'add', data=data)
        else:
            sevlevels = {'info': 0, 'low': 1, 'medium': 2, 'high': 3, 'critical': 4}
            data['severity'] = sevlevels[severity]
            return self.raw_query('recastRiskRule', 'add', data=data)


    def group_add(self, name, restrict, repos, lces=[], assets=[], queries=[],
                  policies=[], dashboards=[], credentials=[], description=''):
        '''group_add name, restrict, repos
        '''
        return self.raw_query('group', 'add', data={
            'lces': [{'id': i} for i in lces],
            'assets': [{'id': i} for i in assets],
            'queries': [{'id': i} for i in queries],
            'policies': [{'id': i} for i in policies],
            'dashboardTabs': [{'id': i} for i in dashboards],
            'credentials': [{'id': i} for i in credentials],
            'repositories': [{'id': i} for i in repos],
            'definingAssets': [{'id': i} for i in restrict],
            'name': name,
            'description': description,
            'users': [],
            'context': ''
        })
