import fields
import debug
import csv
import os
import sys
import datetime

def writer(vulns, **params):
    csvfile = params['fobj']

    debug.write('.')

    for vuln in vulns:
        csvfile.writerow([vuln['name'], vuln['count']])


def gen_csv(sc, filename):
    '''csv SecurityCenterObj, EmailAddress
    '''

    # First thing we need to do is initialize the csvfile and build the header
    # for the file.
    datafile = open(filename, 'wb')
    csvfile = csv.writer(datafile)
    csvfile.writerow(['Software Package Name', 'Count'])

    debug.write('Generating %s: ' % filename)
    # Next we will run the Security Center query.  because this could be a
    # potentially very large dataset that is returned, we don't want to run out
    # of memory.  To get around this, we will pass the query function the writer
    # function with the appropriate fields so that it is parsed inline.
    fparams = {'fobj': csvfile}
    sc.query('listsoftware', func=writer, func_params=fparams)
    debug.write('\n')

    # Lastly we need to close the datafile.
    datafile.close()