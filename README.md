### Python Security Center Module

This module is designed to attempt to make interfacing with Security Center's
API easier to use and more managable.  A lot of effort has been put into making
queries into the API as painless and managable as possible.

__NOTE:__ This rewrite is under active development.  The current functionality
		  is not feature-complete.

### How to use

The new interface is designed to be a lot easier to use than the previous one.
While currently there are fewer functions to present the data back to you, what
has been coded so far has been expresly designed with usability in mind.  Below
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