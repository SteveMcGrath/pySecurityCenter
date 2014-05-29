#!/usr/bin/env python
# Repo Sizes
# ----------
# A simple script to output the current sizes of all of the repositories.  This
# is useful in tracking repository sizes to stave off any potential issues with
# scan imports down the road.
# ----------
# Example Output
# ----------
# [root@securitycenter ~]# ./repo_sizes.py
#                                     IP Count     Raw Size    NSR Size
#                                     --------    ---------   ---------
#   1: Active                            117         24.14M      18.34M
#   2: Compliance                         69         74.49M      32.55M
#   3: Passive                            28          0.02M      14.50M
#   4: Web Applications                    4          0.18M       0.19M
#   5: Ad-Hoc                              2          0.01M       0.02M
#   6: Offline                          4853         89.72M     120.97M
#   7: Traceroutes                         0          1.06M       0.00M
from securitycenter.v1 import SecurityCenter
import os

# Define the needed information to login to the api
username = 'ADMINUSERNAME'
password = 'PASSWORD'
hostname = 'localhost'
convert = 1024 * 1024               # This will convert bytes to Megabytes
                                    #   in base 1024.
unit = 'M'                          # The unit notation (if any)
path = '/opt/sc4/repositories'      # Base path for repositories

# Here we will instantiate the Security Center module
sc = SecurityCenter(hostname, username, password)

# Before we do anything, lets print the header information.
print ' ' * 40 + 'IP Count\t Raw Size\t NSR Size'
print ' ' * 40 + '--------\t---------\t---------'

# First we will get the list of repositories that SC4 is aware of, then
# iterate through them.
for repo in sc.repositories()['repositories']:
    # First we get the filesize of the raw database in bytes.
    raw_size = os.path.getsize('%s/%s/hdb.raw' % (path, repo['id']))

    # Next is the filesize of the nsr file in bytes.  As it is possible for the
    # NSR file to not exist, if there is no file, we will just set it to 0 bytes
    try:
        nsr_size = os.path.getsize('%s/%s/hdb.nsr' % (path, repo['id']))
    except OSError:
        nsr_size = 0

    # Lastly, lets print this stuff out to stdout ;)
    print '%3d: %-30s\t%6d\t\t%8s%s\t%8s%s' % (
        int(repo['id']), repo['name'], int(repo['ipCount']),
        '%.2f' % float(float(raw_size) / convert), unit,
        '%.2f' % float(float(nsr_size) / convert), unit)
