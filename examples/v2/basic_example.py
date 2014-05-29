#!/usr/bin/env python
# Example Python Security Center Script

from securitycenter import Client

# Provide the login info & security center address here:
username = 'api_user'
password = 'secret'
url = 'https://127.0.0.1'
cert = None
verify = False

# Instantiate a Security Center instance and login with the credentials
# provided
sc = Client(url, username, password, cert, verify)

# Now to query the api for vulnerabilities that have publicly known exploits
# with high or critical severity and only look for active vulns (no PVS).
vulns = sc.vuln.query('vulndetails', exploitAvailable='true',
                      pluginType='active', severity='3,4')

# If we simply wanted to print the IP & Vulnerability name, we could uncomment
# this code below and run this...
#for vuln in vulns:
#    print vuln['ip'], vuln['pluginName']

# However I was thinking we could generate something a little nicer, so we will
# run through all of the data and parse it into a tiered dictionary like the
# example here:
# ips = {
#   '127.0.0.1': [{VULNERABILITY DICT}, {VULNERABILITY DICT}],
#   '127.0.0.2': [{VULNERABILITY DICT}, {VULNERABILITY DICT}],
# }

# Generate IP dictionary from the vulnerability data...
ips = {}
for vuln in vulns:
    ips.setdefault(vuln['ip'], []).append(vuln)

# Now to print the output to the screen.  This could easily be rewritten to
# output to a file as well, or even parse it into a CSV file if needed.
for ip, vulns in ips.iteritems():
    print 'IP Address: {0}'.format(ip)
    for vuln in vulns:
        print '\t{0}'.format(vuln['pluginName'])
        # We could also output the pluginText as well if we wanted, however it
        # was too wordy for this example.

# There is a lot more that can be done with the API, and if you need more detail
# I would highly recommend you look at the API documentation and use this
# example as a reference.
