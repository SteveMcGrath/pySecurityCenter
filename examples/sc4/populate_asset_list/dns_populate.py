#!/usr/bin/env python
# SecurityCenter DNS File Uploader
# Version 1.0
# Date: 02/11/2015
from securitycenter import SecurityCenter4
import getpass


def update(sc, filename, asset_id):
    '''
    Updates a DNS Asset List with the contents of the filename.  The assumed
    format of the file is 1 entry per line.  This function will convert the
    file contents into an array of entries and then upload that array into
    SecurityCenter.
    '''
    addresses = []
    with open(filename) as hostfile:
        for line in hostfile.readlines():
            addresses.append(line.strip('\n'))
    sc.asset_update(asset_id, dns=addresses)

if __name__ == '__main__':
    host = raw_input('SecurityCenter Address : ')
    username = raw_input('Username : ')
    password = getpass.getpass('Password : ')
    filename = raw_input('DNS Asset List File : ')
    asset_id = raw_input('Asset List ID : ')
    sc = SecurityCenter4(host)
    sc.login(username, password)
    update(sc, filename, asset_id)