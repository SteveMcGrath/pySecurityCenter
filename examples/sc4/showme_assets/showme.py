#!/usr/bin/env python
from securitycenter import SecurityCenter4

# Please fill out the information below
username = 'USERNAME'
password = 'PASSWORD'
host = 'HOSTNAME OR IP ADDRESS'

sc = SecurityCenter4(host)
sc.login(username, password)

assets = sc.assets()

print 'Repositories\n------------'
for repo in assets['repositories']:
    print repo['id'], repo['name']

print '\nAssets\n------'
for asset in assets['assets']:
    print asset['id'], asset['name']
