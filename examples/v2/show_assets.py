#!/usr/bin/env python
from securitycenter import Client

# Please fill out the information below
username = 'api_user'
password = 'secret'
url = 'https://127.0.0.1'
cert = None
verify = False

sc = Client(url, username, password, cert, verify)

repos = sc.repository.init()
assets = sc.asset.init()

print 'Repositories\n------------'
for repo in repos:
    print repo['id'], repo['name']
print
print 'Assets\n------'
for asset in assets:
    print asset['id'], asset['name']
