#!/usr/bin/env python
import securitycenter
import csv

# Please fill out the information below
username = 'USERNAME'
password = 'PASSWORD'
host = 'HOSTNAME OR IP ADDRESS'

# Now to connect to the SC Instance
sc = securitycenter.SecurityCenter(host, username, password)

# And lets go ahead and build a asset list dictionary to link
# the asset list names to their respective IDs.
assets = {}
for item in sc.assets()['assets']:
	assets[item['name']] = item['id']

# Now lets go ahead and iterate through the CSV file that we have
# on hand.  The format is the following with no header:
# "Asset List Name","DNS1,DNS2,DNS3"
for line in csv.reader(open('example.csv', 'r')):
	sc.asset_update(assets[line[0]], dns=line[1].split(','))