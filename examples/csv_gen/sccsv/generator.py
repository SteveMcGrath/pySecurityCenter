import fields
import debug
import csv
import os
import sys
import datetime

def writer(vulns, **params):
    csvfile = params['fobj']
    flist = params['flist']

    debug.write('.')

    for vuln in vulns:
        # First thing before we do any parsing is we need to generate the
        # firstSeenDate and lastSeenDate fields into the vulnerability
        # dictionary.  These may be requested by the field listing later on.
        fsd = datetime.date.fromtimestamp(int(vuln['firstSeen'])).strftime('%D')
        lsd = datetime.date.fromtimestamp(int(vuln['lastSeen'])).strftime('%D')
        vuln['firstSeenDate'] = fsd
        vuln['lastSeenDate'] = lsd

        # Next we will expand the vulnerability dictionary further thanks to the
        # regexes in the fields dictionary.
        for field in flist:
            if field not in vuln and 'rex' in fields.fields[field]:
                res = fields.fields[field]['rex'].findall(vuln['pluginText'])
                if len(res) > 0:
                    vdata = res[0]
                else:
                    vdata = ''
                vuln[field] = vdata

        # Now that we have everything populated, lets go ahead and build and
        # then write the row to disk.
        row = []
        for field in flist:
            row.append(vuln[field].replace('\\n', '\n'))
        csvfile.writerow(row)


def gen_csv(sc, filename, field_list, source, filters):
    '''csv SecurityCenterObj, AssetListName, CSVFields, EmailAddress
    '''

    # First thing we need to do is initialize the csvfile and build the header
    # for the file.
    csvfile = csv.writer(open(filename, 'wb'))
    header = []
    for field in field_list:
        header.append(fields.fields[field]['name'])
    csvfile.writerow(header)

    debug.write('Generating %s: ' % filename)
    # Next we will run the Security Center query.  because this could be a
    # potentially very large dataset that is returned, we don't want to run out
    # of memory.  To get around this, we will pass the query function the writer
    # function with the appropriate fields so that it is parsed inline.
    fparams = {'fobj': csvfile, 'flist': field_list}
    sc.query('vulndetails', source=source, 
             func=writer, func_params=fparams, **filters)
    debug.write('\n') 