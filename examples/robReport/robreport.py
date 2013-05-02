import securitycenter
import csv
import sys

# Do we want to output debugging information to the screen?  In this case this
# means any output to the screen.
DEBUG = True

# This option here will tell the script to generate a debug log.  This can get
# very big very quickly, so it's recommended to leave this as False.
DEBUGLOG = False

# The User-name that we will be connecting to the SecurityCenter API with.
USERNAME = 'steve'

# The Password for that associated user.
PASSWORD = 'p@ssw0rd'

# The Host-name or IP Address of the Security Center Instance.
SCHOST = 'securitycenter'

# The filters that we will be running to pear-down the dataset.  If you want
# everything, just leave the curly braces {}.  For information on what kind of
# filters you can set, please refer to the API manual.
#
# NOTE: It is HIGHLY recommended that you at the minimum set the severity to
# exclude informational.  To do this add the following into the dictionary:
#  "severity": "4,3,2,1",
SCFILTERS = {
    "exploitAvailable": "true", 
    "pluginType": "active",
    "repositoryIDs": "1",
}

# The filename of the output file.
OUTFILE = 'output.csv'


#### DO NOT MODIFY BELOW THIS LINE UNLESS YOU KNOW WHAT YOU ARE DOING!!! #####
# I did try to document this script as best as I could, however keep in mind
# that if you alter this script, you can potentially break it.  Please get
# yourself acquainted with the API output format before meddling in here.

# Base Dictionary for the IP Database.  This will grow organically as we read
# the vulnerability information.
ipdata = {}

# A simple hash to relate repository IDs to repository names.  This is
# populates before the main call.
repodata = {}

# a simple row counter
rowcount = 0


def debug(msg):
    '''Debug Output Function.  
    Writes msg variable to stdout, bypassing the output buffer.  Will only
    actually write out if the debug flag is set to True.
    '''
    if DEBUG:
        sys.stdout.write(msg)
        sys.stdout.flush()

def writer(vulns, **params):
    '''CSV writer
    This function is what is actually doing all of the heavy lifting.  This
    will be called for every API call and will parse through the data from that
    call.  We are handling the data parsing in-line like this because it's
    entirely possible that we will be batching big jobs into a CSV file. and
    don't want to run out of memory.
    '''
    global rowcount, ipdata, repodata
    csvfile = params['f']   # Get the CSV File object
    sc = params['sc']       # Also make sure to get the sc api object.
    debug('.')              # Lastly, note the API call with a . to the screen.


    for vuln in vulns:       
        # First check to see if we have any existing IP Data on file for this
        # IP.  If not then call in the data.
        if vuln['ip'] not in ipdata:
            ipdata[vuln['ip']] = sc.ip_info(vuln['ip'])['records']

        # Next we need to find the OS for this repository.  As it's possible
        # for overlapping IP space, we need to check for a repository match
        # before we pull anything.
        osname = ''
        for ipd in ipdata[vuln['ip']]:
            if ipd['repositoryID'] == vuln['repositoryID']:
                # only pull the first OS mentioned, which is also the most
                # likely.
                osname = ipd['os'].strip('<br/>').split('\n')[0]

        # And lets compile the row information and write to the file...
        rowcount += 1
        csvfile.writerow([
            vuln['dnsName'],                # DNS Name
            vuln['pluginName'],             # Vulnerability Name
            vuln['baseScore'],              # CVSS Base Score
            osname,                         # Operating System
            repodata[vuln['repositoryID']]  # Repository Name
        ])


def gen_csv(username, password, host, filters, filename='output.csv'):
    '''gen_csv
    This is the wrapper function that will perform the needed initialization
    and initiate the query to the API.
    '''

    # Open the datafile (CSV File) and wrap that into a csv writer.
    datafile = open(filename, 'wb')     
    csvfile = csv.writer(datafile)

    # Next we need to output the header.
    csvfile.writerow(['DNS Name', 'Vulnerability Name', 'CVSS Base Score',
                      'Operating System', 'Repository'])

    # From here on, follow the debug statements ;)
    debug('* Logging into Security Center...\n')
    sc = securitycenter.SecurityCenter(host, username, password, debug=DEBUGLOG)
    
    debug('* Populating Repository Data...\n')
    for item in sc.assets()['repositories']: 
        repodata[item['id']] = item['name']
    
    debug('* Initiating Query...\nx100 Rows: ')
    sc.query('vulndetails', func=writer, req_size=100,
             func_params={'f': csvfile, 'sc': sc}, **filters)
    debug('\nRows: %s\n' % rowcount)

    # Lastly we need to close the datafile.
    datafile.close()


if __name__ == '__main__':
    gen_csv(USERNAME, PASSWORD, SCHOST, SCFILTERS, OUTFILE)