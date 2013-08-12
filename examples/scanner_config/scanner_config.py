#!/usr/bin/env python
from securitycenter.v1 import SecurityCenter
import sys
import csv


def get_scanners(sc):
    '''Returns the Configured Scanners within Security Center'''
    scanners = {}
    for item in sc.raw_query('scanner','init')['scanners']:
        scanners[item['ip']] = {'name': item['name'], 'id': item['id']}
    return scanners


def new_scanner(ip, name, username, password):
    '''Adds a new scanner into Security Cneter'''
    sc.raw_query('scanner','add', {
        'context': '',
        'authType': 'password',
        'verifyHost': 'false',
        'ip': ip,
        'port': 8834,
        'username': username,
        'password': password,
        'useProxy': 'false',
        'name': name,
        'description': '',
        'enabled': 'true',
        })
    print 'INFO: Adding Scanner: %s/%s' % (name, ip)


def new_zone(name, ip_range, scanners=[]):
    '''Adds a new Zone into Security Center'''
    sc.raw_query('zone', 'add', {
        'name': name,
        'ipList': ip_range,
        'description': '',
        'scanners': [{'id': s} for s in scanners]
        })
    print 'INFO: Adding Zone %s with %s scanners' % (name, len(scanners))


def mass_import(filename, username, password, sc):
    '''Mass Importer
    This function will read a CSV file specified and use the username & password
    provided for the scanners to configure all scanners and zones that have
    been supplied.

    CSV File Format:
    Scanner Name,Scanner IP,Zone Name,Zone Ranges
    Scanner 1,127.0.0.1,Test Zone,127.0.0.0/8

    * The Header is assumed to be there, however the header is not parsed.  This
      may cause issues if you start the data on line 1.  Always start data on
      line 2.
    * The CSV file should never have more than 4 Cells to a row.  If more do
      exist, problems will likely occur.
    '''
    zones = {}  # This is the zones dictionary.  It will be populated as we
                # move along.
    # Open the CSV file and skip past the header.
    reader = csv.reader(open(filename, 'rb'))
    reader.next()
    for row in reader:
        # First lets pull the 4 cells that we are interested in and populate
        # them into the appropriate variables.
        sname, sip, zname, zrange = row

        # A simple check to make sure that the Scanners Cells are not blank.
        # It's entirely possible to create orphaned zones in this way.  This
        # could be useful for just populating the zones.
        if sname is not '' and sip is not '':
            # In this block we will get the currently configured scanners in
            # SecurityCenter and only add in the configured scanner if it does
            # not exist already.
            scanners = get_scanners(sc)
            if sip not in scanners:
                new_scanner(sip, sname, username, password)

        # Again the same kinda check here, we need to make sure that the Zone
        # specific entries are not blank.  This again allows for the creation
        # scanners that have no zones in them if needed by simply blanking out
        # these lines.
        if zname is not '' and zrange is not '':
            # If the Zone is not already known to us, then add it in.
            if zname not in zones:
                zones[zname] = {'scanners': [], 'ranges': []}

            # If we have a configured scanner, then lets add it to the zone
            # as well.
            if sname is not '' and sip is not '':
                zones[zname]['scanners'].append(sip)

            # Also lets append the configured ranges to the zone as well.
            zones[zname]['ranges'].append(zrange)
    scanners = get_scanners(sc)

    # Lastly, we need to add all of the zones.  As we already have been adding
    # the scanners as we move along, these should be simple inserts into the
    # API.
    for zone in zones:
        sids = []
        for scanner in zones[zone]['scanners']:
            sids.append(scanners[scanner]['id'])
        new_zone(zone, ','.join(zones[zone]['ranges']), sids)


if __name__ == '__main__':
    scip = raw_input('Enter Address for SecurityCenter : ')
    scpass = raw_input('Enter SecurityCenter Admin Password : ')
    try:
        sc = SecurityCenter(scip, 'admin', scpass)
    except:
        print 'ERROR: Authentication Failed.'
        sys.exit()

    filename = raw_input('Enter CSV Filename with Scan Zones/Scanners : ')
    username = raw_input('Enter Username for Scanners : ')
    password = raw_input('Enter Password for Scaners : ')
    mass_import(filename, username, password, sc)
