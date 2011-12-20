#!/usr/bin/env python
# CSV Report Generator
# --------------------
# This script is designed to pull vulnerability data from Security Center 4.2
# and format it into a CSV file.  While Security Center can already do this,
# this script will also break out the Plugin Text field into individial fields
# before generating the CSV row.  Once the report has been generated, the
# script will then compile and email and send the email off to the email
# associated to the asset list in question.
# --------------------
#
# Written By: Steven McGrath
# Verison: Build 023
# Date: 09/01/2011

from securitycenter import SCBase
from ConfigParser import ConfigParser
from email.MIMEMultipart import MIMEMultipart
from email.MIMEBase import MIMEBase
from email.MIMEText import MIMEText
from email.Utils import formatdate
from email import Encoders
import smtplib
import re
import csv
import zipfile
import os
import datetime

# Listing of all of the available fields that will be allowed to pull from
# the vulnerability data returned.
plugin_fields = {
    'ip': {'name': 'IP Address'},
    'netbiosName': {'name': 'NetBIOS Name'},
    'dnsName': {'name': 'DNS Name'},
    'macAddress': {'name': 'Hardware Address'},
    'pluginID': {'name': 'Plugin ID'},
    'pluginName': {'name': 'Plugin Name'},
    'severity': {'name': 'Severity'},
    'port': {'name': 'Port'},
    'pluginText': {'name': 'Plugin Text'},
    'firstSeen': {'name': 'Days Since Discovered'},
    'lastSeen': {'name': 'Days Since Seen'},
    'firstSeenDate': {'name': 'Date Discovered'},
    'lastSeenDate': {'name': 'Date Last Seen'},
    
    # Builtin Additional Fields
    'pluginSynopsis': {
        'name': 'Synopsis', 
        'rex': re.compile(r'Synopsis :\\n\\n(.*?)\\n\\n'),
    },
    'pluginDescription': {
        'name': 'Description',
        'rex': re.compile(r'Description :\\n\\n(.*?)\\n\\n'),
    },
    'pluginSeeAlso': {
        'name': 'See Also',
        'rex': re.compile(r'See also :\\n\\n(.*?)\\n\\n'),
    },
    'pluginSolution': {
        'name': 'Solution',
        'rex': re.compile(r'Solution :\\n\\n(.*?)\\n\\n'),
    },
    'pluginRiskFactor': {
        'name': 'Risk Factor',
        'rex': re.compile(r'Risk factor :\\n\\n(.*?)\\n\\n'),
    },
    'pluginCVE': {
        'name': 'CVE',
        'rex': re.compile(r'CVE : (.*?)\\n'),
    },
    'pluginBID': {
        'name': 'BID',
        'rex': re.compile(r'BID : (.*?)\\n'),
    },
    'pluginOtherRefs': {
        'name': 'Other References',
        'rex': re.compile(r'Other references : (.*?)\\n'),
    },
    'pluginCVSS': {
        'name': 'CVSS Score',
        'rex': re.compile(r'CVSS Base Score : (.*?)\\n'),
    },
    
    # Custom Fields go here.
}

# Replacement dictionary for Severity
severity = {
    0: 'Low',
    1: 'Medium',
    2: 'High',
    3: 'Critical',
}

# Initialize any static variables.
CONFIG = os.path.join(os.path.dirname(__file__), 'config.ini')
FILES = os.path.join(os.path.dirname(__file__), 'files')

# Initialize and read in the configuration file.
config = ConfigParser()
config.read(os.path.join(os.path.dirname(__file__), 'config.ini'))
DEBUG = config.getboolean('Security Center', 'debug')
if DEBUG:
    print 'Using Config file: %s' % CONFIG
    print 'Using File directory %s' % FILES

# First thing, we need to connect to the SC4 installation.  We will use the
# username and password that we have specified in the configuration file to
# connect.
if DEBUG: print 'Logging into Security Center...'
sc = SCBase(config.get('Security Center', 'username'),
            config.get('Security Center', 'password'),
            config.get('Security Center', 'host'),
            port=config.getint('Security Center', 'port'))

# Now we need to get the asset lists that are in Security Center so that we
# have something to lookup against.
if DEBUG: print 'Polling Security Center for Asset Lists...'
sc_assets = sc.assets()['response']['assets']

# Next we need to generate a list of the asset lists configured in the config
# file.
asset_lists = []
for section in config.sections():
    if section[:7] == 'ASSET: ':
        if DEBUG:
            print 'Config File had %s' % config.get(section, 'name')
        asset_lists.append(section)

# Next we really start working.  This loop handles most of the heavy lifting.
for asset_list in asset_lists:
    # First we need to match the asset list name that we have from the
    # configuration file and match it with the asset lists that we pulled from
    # Security Center
    asset = None
    for sc_asset in sc_assets:
        if sc_asset['name'] == config.get(asset_list, 'name'):
            if DEBUG: print 'Starting %s.' % sc_asset['name']
            asset = sc_asset
    
    # The CSV File
    csv_count = 0
    out = csv.writer(open(os.path.join(FILES, 
                                    '%s.csv' % asset['name']), 'wb'))

    # Get field listing from the config file.
    fields = []
    for field in config.get(asset_list, 'fields').split(','):
        if field.strip() in plugin_fields:
            fields.append(field.strip())
    
    # Generate the CSV Header row.
    dset = []
    for field in fields:
        dset.append(plugin_fields[field]['name'])
    out.writerow(dset)
    #out.writerow(['IP Address', 'NetBIOS Name', 'DNS Name', 'Hardware Address',
    #              'Plugin ID', 'Plugin Name', 'Severity', 'Port', 'Synopsis',
    #              'Description', 'See Also', 'Solution', 'CVE', 'CVSS',
    #              'Other References', 'Plugin Text'])
    
    # Next we need to run the query to pull all of the vulnerability data that
    # we are looking for.  Because of how Security Center is designed, we will
    # need to pull a rotating window of data
    api_count = 0
    vulns = []
    increm = config.getint('Security Center', 'request_size')
    if DEBUG: print 'Querying Security Center via API...'
    while len(vulns) == increm or api_count == 0:
        vulns = sc.vuln_search(tool='vulndetails',
                                 acceptedRisk=False,
                                 wasMitigated=False,
                                 startOffset=api_count,
                                 endOffset=api_count + increm,
                                 sourceType='cumulative',
                                 filters=[{
                                    'filterName': 'assetID',
                                    'value': asset['id'],
                                    'operator': '='}]
                                )['response']['results']
        api_count += increm
        if DEBUG: print '.',
        for vuln in vulns:
            csv_count += 1
        
            # Before we can save out the data for the row, we first need to 
            # parse out the known data in the pluginText field.  This means 
            # that we will be iterating through the breakdown list and adding 
            # the discovered data to the dictionary.
            for item in plugin_fields:
                if item not in vuln and 'rex' in plugin_fields[item]:
                    data = plugin_fields[item]['rex'].findall(vuln['pluginText'])
                    if len(data) > 0:
                        vdata = data[0]
                    else:
                        vdata = ''
                    vuln[item] = vdata
            
            # New we need to add the appropriate date fields.
            vuln['firstSeenDate'] = datetime.date.\
                        fromtimestamp(int(vuln['firstSeen'])).strftime('%D')
            vuln['lastSeenDate'] =  datetime.date.\
                        fromtimestamp(int(vuln['lastSeen'])).strftime('%D')
            
            # Watch out, it's row writing time!
            dset = []
            for field in fields:
                dset.append(vuln[field].replace('\\n', '  '))
            out.writerow(dset)
    
    if DEBUG: print '\nWrote %d Lines\n' % csv_count,
    
    # This is a shortcut for an asset.  If the gen_email declaration in the
    # configuration file is set to false, then we will not bother with
    # compressing the csv file and email that out.
    if not config.getboolean(asset_list, 'gen_email'):
        continue
    
    # Next we compress the CSV file we have just created so that it is prepped
    # to be emailed out.
    if DEBUG: print 'Compressing %s.csv to %s.zip...' % (asset['name'],
                                                         asset['name'])
    with zipfile.ZipFile(os.path.join(FILES, 
                         '%s.zip' % asset['name']), 'w') as zfile:
        zfile.write(os.path.join(FILES,
                    '%s.csv' % asset['name']), 
                    '%s.csv' % asset['name'])
    
    # Now we start working on generating the email that we will be sending out
    # to the user.
    if DEBUG: print 'Generating Email message...'
    
    # The first part of generating the email is to parse all of the config
    # settings and dump them into the msg object that we have created.
    msg = MIMEMultipart()
    msg['From'] = config.get('SMTP', 'from_addr')
    msg['To'] = config.get(asset_list, 'email')
    msg['Date'] = formatdate(localtime=True)
    msg['Subject'] = config.get('SMTP', 'subject')
    msg.attach(MIMEText(config.get('SMTP', 'body')))
    
    # The next stage it to build & attach the zipfile we just created to the
    # email message object.
    part = MIMEBase('application', 'octet-stream')
    part.set_payload(open(os.path.join(FILES,
                     '%s.zip' % asset['name']), 'rb').read())
    Encoders.encode_base64(part)
    part.add_header('Content-Disposition', 
                    'attachment; filename="%s.zip"' % asset['name'])
    msg.attach(part)
    
    # Lastly, we need to send the email...
    smtp = smtplib.SMTP(config.get('SMTP', 'host'))
    smtp.sendmail(config.get('SMTP', 'from_addr'), 
                  config.get(asset_list, 'email').split(','),
                  msg.as_string())
    smtp.close()