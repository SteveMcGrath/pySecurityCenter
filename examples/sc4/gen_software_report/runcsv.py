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
# Verison: Build 042
# Date: 05/01/2012

import sccsv
import securitycenter
import json
import os
from ConfigParser import ConfigParser

conf = ConfigParser()
conf.read('csv_gen.conf')

sccsv.debug.DEBUG = conf.getboolean('Settings', 'debug')

sc = securitycenter.SecurityCenter(conf.get('Settings', 'address'),
                                   conf.get('Settings', 'username'),
                                   conf.get('Settings', 'password'),
                                   port=conf.getint('Settings', 'port'))


def build_and_email(section):
    # The first thing that we need to do is get all of the email configuration
    # stuff loaded up.  This will involve some minor parsing and in some cases
    # we will need to check to see if there is a local variable set to override
    # the global one that is set in the Settings stanza.
    email_to = conf.get(section, 'email_to').split(',')
    email_from = conf.get('Settings', 'email_from')
    email_host = conf.get('Settings', 'smtp_host')
    if conf.has_option(section, 'email_msg'):
        email_msg = conf.get(section, 'email_msg')
    else:
        email_msg = conf.get('Settings', 'email_msg')
    if conf.has_option(section, 'email_subject'):
        email_subject = conf.get(section, 'email_subject')
    else:
        email_subject = conf.get('Settings', 'email_subject')

    # We are going to derrive the filename from the stanza...
    filename = '%s.csv' % section.replace('CSVFILE: ', '')

    # Now that we have everything in place, it's time to call the worker
    sccsv.generator.gen_csv(sc, filename)

    # Now that we have the CSV file generated, check to see if we want to
    # send out an email and act accordingly.  If we do generate an email, then
    # we will delete the CSV file when done, otherwise just leave it.
    if conf.getboolean(section, 'gen_email'):
        sccsv.mail.send(email_from, email_to, email_subject, email_msg,
                        filename, host=email_host)
        os.remove(filename)


if __name__ == '__main__':
    for section in conf.sections():
        if 'CSVFILE: ' in section:
            build_and_email(section)