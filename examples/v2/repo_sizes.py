#!/usr/bin/env python
"""Repo Sizes

A simple script to output the current sizes of all of the repositories.  This
is useful in tracking repository sizes to stave off any potential issues with
scan imports down the road.

[root@securitycenter ~]# ./repo_sizes.py
                                    IP Count     Raw Size    NSR Size
                                    --------    ---------   ---------
  1: Active                            117         24.14M      18.34M
  2: Compliance                         69         74.49M      32.55M
  3: Passive                            28          0.02M      14.50M
  4: Web Applications                    4          0.18M       0.19M
  5: Ad-Hoc                              2          0.01M       0.02M
  6: Offline                          4853         89.72M     120.97M
  7: Traceroutes                         0          1.06M       0.00M
"""

from __future__ import division
import os
from securitycenter import Client

# Define the needed information to login to the api
username = 'api_user'
password = 'secret'
host = 'https://127.0.0.1'
cert = None
verify = False

convert = 1024 ** 2 # This will convert bytes to Megabytes in base 1024.
unit = 'M' # The unit notation (if any)
path = '/opt/sc4/repositories' # Base path for repositories

# Here we will instantiate the Security Center module
sc = Client(host, username, password, cert, verify)

# Before we do anything, lets print the header information.
print ' ' * 40 + 'IP Count\t Raw Size\t NSR Size'
print ' ' * 40 + '--------\t---------\t---------'

# First we will get the list of repositories that SC4 is aware of, then
# iterate through them.
for repo in sc.repository.init():
    # First we get the filesize of the raw database in bytes.
    raw_size = os.path.getsize(os.path.join(path, repo['id'], 'hdb.raw'))

    # Next is the filesize of the nsr file in bytes.  As it is possible for the
    # NSR file to not exist, if there is no file, we will just set it to 0 bytes
    try:
        nsr_size = os.path.getsize(os.path.join(path, repo['id'], 'hdb.nsr'))
    except OSError:
        nsr_size = 0

    # Lastly, lets print this stuff out to stdout
    print '{0:3d}: {1: <30}\t{2:6d}\t\t{3:8.2f}{5}\t{4:8.2f}{5}'.format(
        int(repo['id']), repo['name'], int(repo['ipCount']),
        raw_size / convert, nsr_size / convert, unit)
