Security Center for Python
==========================

Wrap the Security Center API to make connections and queries easier to use.
Handles managing sessions, SSL, and processing responses so you can spend more
time getting the data you want.

How to Install
--------------

Use pip to install a release from PyPI::

    pip install pySecurityCenter

Or install the latest master from GitHub::

    pip install https://github.com/SteveMcGrath/pySecurityCenter/archive/master.zip

Basic Usage
-----------

Create a SecurityCenter instance to log in.  API "modules" are attributes on
the instance.  API "actions" are methods on the modules. ::

    >>> from securitycenter import Client
    >>> sc = Client("host", "user", "pass")
    >>> ips = sc.vuln.query("sumip")["results"]
    >>> len(ips)
    240
    >>> ips[0]
    {u'macAddress': '', u'severityHigh': u'0', u'severityMedium': u'3',
    u'ip': u'10.10.0.1', u'netbiosName': '', u'repositoryID': u'1',
    u'severityCritical': u'0', u'score': u'47', u'severityLow': u'38',
    u'total': u'41', u'dnsName': u'pfsense.home.lan', u'severityInfo': u'0'}

SSL Support
^^^^^^^^^^^

The Requests library supports both server verification and sending a client
certificate for two-way SSL. ::

    # verification, system trust chain
    Client("host", verify=True)

    # verification, custom trust chain
    Client("host", verify="path/to/chain")

    # two-way
    # cert can be combined public and private, or (pub, priv) tuple
    Client("host", cert="path/to/cert", verify="path/to/chain")

Security Center can log in a user based on a client certificate instead of a
username and password.  To enable that, first log in with a username and
password while providing a certificate, then register the certificate. ::

    sc = Client("host", "user", "pass", cert="path/to/cert")
    sc.auth.save_fingerprint()

Available Modules
-----------------

.. warning:: Not all of the modules and actions are officially documented.

- admin
- asset
- auth
- credential
- file
- heartbeat
- message
- nessusResult
- plugin
- policy
- report
- reportResult
- repository
- role
- scan
- scan_result
- system
- user
- vuln
- zone
