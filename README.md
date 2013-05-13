# Python Security Center Module

This module is designed to attempt to make interfacing with Security Center's
API easier to use and more manageable.  A lot of effort has been put into making
queries into the API as painless and manageable as possible.

__NOTE:__ This rewrite is under active development.  The current functionality,
		      while feature-complete, can potentially change at any time.

# How to Install

To install pySecurityCenter, you can use either pip or easy_install to install
from the cheeseshop:

`pip install pysecuritycenter`

`easy_install pysecuritycenter`

If you would rather install manually, feel free to download the latest version
directly from the [cheeseshop][]:

[cheeseshop]: http://pypi.python.org/pypi/pySecurityCenter

# How to use

The new interface is designed to be a lot easier to use than the previous one.
While currently there are fewer functions to present the data back to you, what
has been coded so far has been expressly designed with usability in mind.  Below
is a basic example showing the result of the sumip tool:

	>>> import securitycenter
	>>> sc = securitycenter.SecurityCenter('ADDRESS','USER','PASS')
	>>> ips = sc.query('sumip', repositoryIDs='1')
	>>> len(ips)
	240
	>>> ips[0]
	{u'macAddress': '', u'severityHigh': u'0', u'severityMedium': u'3', 
	u'ip': u'10.10.0.1', u'netbiosName': '', u'repositoryID': u'1', 
	u'severityCritical': u'0', u'score': u'47', u'severityLow': u'38', 
	u'total': u'41', u'dnsName': u'pfsense.home.lan', u'severityInfo': u'0'}

By default, the query function will perform as many queries to the API as needed
to pull all of the data and return all of the information as a single list.
There are cases however where the dataset that is returned back may be too large
to load everything into memory.  In this case there is the option to pass a
function to the API to handle the data for you.  In this case, the API will not
populate the list that will be returned back.  Below is an example of how this
works:

	>>> import securitycenter
	>>> def count(data):
	...     print len(data)
	... 
	>>> sc = securitycenter.SecurityCenter('ADDRESS','USER','PASS')
	>>> sc.query('sumip', func=count, repositoryIDs='1')
	240
	[]

One of the nice things about the query function is that we can also use it to
parse LCE event data as well.  For example:

	>>> import securitycenter
	>>> sc = securitycenter.SecurityCenter('ADDRESS','USER','PASS')
	>>> events = sc.query('sumip', source='lce')
	>>> len(events)
	425

For other functions, please use the raw_query function until the functions have
been rewritten.  For detailed documentation for the various other things that
can be done, please reference the Security Center API documentation.

# Available Functions

## raw_query

__Required Inputs:__ module, action

__Optional Inputs:__ data, headers, dejson

### Info

The raw_query function is the most basic function exposed for general use.  This
function is simply a thin wrapper around the private _request function and
will strip out information higher on the return tree than the response.  If
an error code is thrown, then it will throw an APIError exception with the 
error code and the error message.  All other public functions route calls
through raw_query.

### Usage

	sc.raw_query(module, action, data={}, headers={}, dejson=True)

### Options

* __module:__ [string]<br />
  The API module to be called.  For information on the available modules that
  can be called, please reference the API documentation from Tenable.

* __action:__ [string]<br />
  The API module's action to be called.  For information on the available
  actions that a module may have, please reference the API documentation from
  Tenable.

* __data:__ [dictionary]<br />
  The data dictionary that is placed into the 'input' definition of the JSON
  POST request to the API.  This is highly dependent on the module and action
  being called and information about what should be contained in here is in the
  API documentation from Tenable.

* __headers:__ [dictionary]<br />
  The HTTP headers that will be sent as part of the POST request to the API.
  While publicly exposed, there is almost never a need to add anything into this
  dictionary.

* __dejson:__ [boolean]<br />
  Tells the _request function weather or not we want to convert the HTTP
  response into a python dictionary.  As most responses will be JSON formatted
  strings, this is normally left alone, however there are cases where turning
  this off is needed.  For example when downloading scan results.

## query

__Required Inputs:__ tool

__Optional Inputs:__ filters, source, sort, direction, func, func_params, 
					 req_size, filterset

### Info

The query function is designed to make querying vulnerability and event data
within Security Center as painless as possible.  By handling the vast majority
of the boilerplate code within this function, it is possible to write one line
queries into the API.  This function also merges together querying both
vulnerability and event data as most of the methodology for querying either
dataset is the same.

### Usage

	sc.query(tool, filters=None, source='cumulative', sort=None, direction=None,
			 func=None, func_params=None, req_size=1000, **filterset)

### Options

* __tool__ [string]<br />
  The query tool to be run on the API.  This can be any of the query tools from
  vuln::query or event::query depending on the data source you are using.  These
  tools are the same as when running a search query in the main WebUI.  Refer to
  the API documentation for a list of available tools.

* __filters__ [list]<br />
  If a complex filter is needed (something more than x=y) then you will need to
  populate this list as well.  As per the documentation, the filters list is a
  list of dictionary items detailing the filterName, operator, and value of the
  filter.  Each dictionary item should look like the example below:<br />
  <br />
  `{'filterName': 'exploitAvailable', 'operator': '=', 'value': 'true'}`<br />
  <br />
  Generally speaking this option is available if needed, however should almost
  never be used.  Instead use the less error-prone and more efficient
  **filterset dictionary

* __source__ [string]<br />
  Defines the data source to be used for the query.  There are three options
  available to query from.  Please keep in mind that this variable invariably 
  determines if you will be querying event or vulnerability data and the toolset
  & filterset will be different depending on which data source you query.
	* _cumulative:_ Cumulative vulnerability data
	* _mitigated:_ Mitigated vulnerability data
	* _lce:_ LCE event data

* __sort__ [string]<br />
  Specifies the field name to sort by.  Default is None.

* __direction__ [string]<br />
  If a sort field is specified, then this option will specify the sort direction
  desired.  The default is descending (desc) however ascending (asc) can be
  selected as well.

* __func__ [function]<br />
  If func is defined, it will allow for an alternate way to handle the data that
  is being queried.  Instead of flattening the dataset into a single list, which
  can be problematic for very large datasets, the query function will instead
  send the vuln data directly to a function passed on to it and will not
  populate any data into the list to be returned.  This means that it is
  possible to handle very large datasets in smaller chunks if desired.  For an
  example of how this is used, refer to the CSV_GEN example script.  The
  generator module shows exactly how this would be handled.

* __func_params__ [dictionary]<br />
  An optional dictionary parameter list to be sent to the function defined in
  the func option.  This is useful if more information than just the query data
  needs to be sent to the function for processing.

* __req_size__ [integer]<br />
  How many items to query from the API at a time.  The default is 1000.  Keep in
  mind that larger values may not increase the speed of the API and may actually
  slow down other operations on the Security Center host.  Adjust at your own
  risk.

* __**filterset__ [dictionary]\[parameters]<br />
  Filterset is the catchall for the various filters that can be called for the
  query.  Any filters that you would want to run should be after all other
  options in the query to insure that they are all lumped into this filterset
  dictionary.  as this dictionary is parameterized, there is no need to specify
  the options like in a normal dictionary, instead simply declare them as if
  specifying any other option in the function.  for example:<br />
  <br />
  `sc.query('vulndetails', exploitAvailable='true', severity='2,3,4')`<br />
  <br />
  This query will set the expploitAvailable filter to true and the severity to
  '2,3,4' (Medium, High, and Critical).  As you can see, defining filters this
  way is a lot cleaner than specifying them in the raw format as with the 
  __filters__ dictionary.

## login

__Required Inputs:__ user, passwd

__Optional Inputs:__ NONE

### Info

Performs the login sequence into the API and stored the authentication token for
future use.  Generally this function does not need to be called as it normally
run as part of the instantiation process for a SecurityCenter object.

### Usage

	sc.login('USERNAME', 'PASSWORD')

### Options

* __user__ [string]<br />
  Username of the user to authenticate with.

* __passwd__ [string]<br />
  Password fo the user to authenticate with.

## logout

__Required Inputs:__ NONE

__Optional Inputs:__ NONE

### Info

Performs a logout on the API and drops the token from the authentication cache.

### Usage

	sc.logout()

## assets

__Required Inputs:__ NONE

__Optional Inputs:__ NONE

### Info

A convenience function to run _asset::init_ on the API.  returns the result to
the caller.

### Usage

	sc.assets()

## asset_update

__Required Inputs:__ asset_id

__Optional Inputs:__ name, description, visibility, group, users, ips, rules

### Info

Updates an asset list with the optional inputs provided.  This function will
first perform an asset list lookup and populate the request to be sent with the
current values, then override those values with what was requested in the
optional parameters.  This means it is possible to only update the ip list, or
description, without having to pull and populate everything else by hand.

### Usage

	sc.asset_update(asset_id, name=None, description=None, visibility=None,
					group=None, users=None, ips=None, rules=None)

### Options

* __asset_id__ [integer]<br />
  The id of the asset list to edit.

* __name__ [string]<br />
  The new name for the asset list.

* __description__ [string]<br />
  The new description for the asset list.

* __visibility__ [string]<br />
  The new visibility setting for the asset list.  The 2 values this can be set
  to is 'organizational' and 'user'.

* __group__ [string]<br />
  The new group name for the asset list.

* __users__ [list]<br />
  A list of the user ids that have access to see this asset list.  Overrides the
  existing settings.

* __ips__ [list]<br />
  A list of IPs, IP ranges, and CIDR ranges to be defined for a static list.
  Setting this will override the existing settings, not append.

* __rules__ [list]<br />
  Will override the existing rules set for this asset list.  This is the raw
  rules definition.

## asset_ips

__Required Inputs:__ asset_id

__Optional Inputs:__ NONE

### Info

Returns the IPs associated with the asset list id defined.

### Usage

	sc.asset_ips(asset_id)

### Options

* __asset_id__ [integer]<br />
  The asset list id to query the API with.

## credendials

__Required Inputs:__ NONE

__Optional Inputs:__ NONE

### Info

Returns a list of the credentials stored within Security Center

### Usage

  sc.credentials()

## cedential_update

__Required Inputs:__ cred_id

__Optional Inputs:__ **options

### Info

Updated the specified credential with the fields specified.

### Usage

  sc.credential_update(cred_id, **options)

### Options

* __cred_id__ [integer]<br />
  The identifier of the credential to be updated.

* __**options__ [dictionary]\[parameters]<br />
  A parameterized dictionary list containing the fields that will be
  updated.  For example, if the name and password of the credential
  is to be updated to 'New Cred 2' and 'Password123' respectively, then
  the following call to the API would be requested:<br />
  <br />
  `sc.credential_update(1, name='New Cred2', password='Password123')`<br />
  <br />

## plugins

__Required Inputs:__ NONE

__Optional Inputs:__ plugin_type, sort, direction, size, offset, all, loops,
                      since, **filterset

### Info

Returns information about the plugins requested.  By default it will
return a list of all of the plugins in the system.

### Usage

  sc.plugins(plugin_type='all', sort='id', direction='asc', size=1000,
             offset=0, all=True, loops=0, since=None, **filterset)

### Options

* __plugn_type__ [string]<br />
  String containing the type of plugins that the user wants returned.  Available
  options are "all", "notPassive", "active", "compliance", "custom", and "passive".
  The default option is "all".

* __sort__ [string]<br />
  String that denotes the field name that you wish to sort by.

* __direction__ [string]<br />
  The direction of the sort.  "asc" and "desc" are valid directions, default is "asc".

* __size__ [integer]<br />
  Number of plugins to query for each request.  Default is 1000.

* __offset__ [integer]<br/>
  Number of plugins to skip at the beginning of the query.  Useful if you want
  to get all results but only store chunks in memory.  Default is 0.

* __all__ [boolean]<br />
  Determins whether we should loop until we have all of the plugin data.

* __loops__ [integer]<br />
  If all is set to "False" then this will dictate the number of loops to complete before
  stopping.  Default is 0.

* __since__ [datetime.datetime or datetime.date]<br />
  If since is specified, only return plugins that have been created/updated since that
  datetime object.

* __**filterset__ [dictionary]\[parameters]<br />
  A Filterset that works similarly to how query's filterset works.  Furthermore any of the
  items in the _xrefs list can be used as well for the filter.

## plugin_counts

__Required Inputs:__ NONE

__Optional Inputs:__ NONE

### Info

Returns a dictionary detailing plugin counts for active, passive, compliance, and
custom plugin types as is available.

### Usage

  sc.plugin_counts()


## plugin_details

__Required Inputs:__ plugin_id

__Optional Inputs:__ NONE

### Info

Returns the details of a specific plugin id.

### Usage

  sc.plugin_details(plugin_id)

### Options

* __plugin_id__ [integer]<br />
  The Plugin ID of the Plugin that is requested.


## repositories

__Required Inputs:__ NONE

__Optional Inputs:__ NONE

### Info

Returns the repository information, license information, and organizational information.

### Usage

  sc.repositories()


## roles

__Required Inputs:__ NONE

__Optional Inputs:__ NONE

### Info

Returns the user roles and associated metadata.

### Usage

  sc.roles()


## tickets

__Required Inputs:__ NONE

__Optional Inputs:__ NONE

### Info

Returns tickets and their associated data.

### Usage

  sc.tickets()


## users

__Required Inputs:__ NONE

__Optional Inputs:__ NONE

### Info

Returns all user information from the Security Center instance.

### Usage

  sc.users()


## vulns

__Required Inputs:__ NONE

__Optional Inputs:__ NONE

### Info

Returns all available vulnerabilities in the Security Center Instance.

### Usage

  sc.vulns()


## ip_info

__Required Inputs:__ ip

__Optional Inputs:__ repository_ids

### Info

Returns information abotu the IP specified in the repository IDs defined.  These details
include things like MAC Address, Hostname, etc.

### Usage

  sc.ip_info(ip, repository_ids=[])

### Options

* __ip__ [string]<br />
  String containing the IP of the host that we want to pull the information for.

* __repository_ids__ [list of integers]<br />
  The Repository IDs that we want to pull the information from.  This is used if we only
  Want information from select repositories, and not all of them.


## zones

__Required Inputs:__ NONE

__Optional Inputs:__ NONE

### Info

Returns all available scan zone and scaner status information.

### Usage

  sc.zones()


## scan_list

__Required Inputs:__ NONE

__Optional Inputs:__ start_time, end_time

### Info

Returns a list of all of the scans stored within Security Center based on the time range
specified.  The default time range is from current to current -30 days.

### Usage

  sc.scan_list(start_time=None, end_time=None)

### Options

* __start_time__ [integer]<br />
  Time in unix epoch time for the most current (forward) boundry of the window.  Default
  is NOW.

* __end_time__ [integer]<br />
  Time in unix epoch time for the least current (backward) boundry of the window.  Default
  is NOW - 30 days.


## scan_download

__Required Inputs:__ scan_id

__Optional Inputs:__ format

### Info

Returns the raw data for the nessus scan id specified.  Optionally the scan data format
can be specified to override the default format returned.

### Usage

  sc.scan_download(scan_id, format='v2')

### Options

* __scan_id__ [integer]<br />
  The unique scan identifier for the scan that we wish to download.

* __format__ [string]<br />
  This string denotes the format fo the data to be returned.  The default for the plugin is
  'v2'.  Depending on the version of Security Center, this information can/will be different.
  For versions of Security Center earlier than 4.4 the options "nsr" and "nessus" are
  available.  For SC4.4, "v1" and "v2" are the options, denoting the .nessus v1 and v2
  formats.  Note that in earlier versions of SC4, "nessus" refers to .nessus v1.


## dashboard_import

__Required Inputs:__ name, filename

__Optional Inputs:__ NONE

### Info

Uploads a dashboard template to the current user's dashboard tabs.

__NOTE:__ This is an un-documented call and is not considered stable.

### Usage

  sc.dashboard_import(name, filename)

### Options

* __name__ [string]<br />
  The name of the dashboard tab once uploaded.

* __filename__ [string]<br />
  The filename and path of the file that will be uploaded.


## report_import

__Required Inputs:__ name, filename

__Optional Inputs:__ NONE

### Info

Uploads a report template to the current user's reports.

__NOTE:__ This is an un-documented call and is not considered stable.

### Usage

  sc.report_import(name, filename)

### Options

* __name__ [string]<br />
  The name of the report once uploaded.

* __filename__ [string]<br />
  The filename and path of the file that will be uploaded.