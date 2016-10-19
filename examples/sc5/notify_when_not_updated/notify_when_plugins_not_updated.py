#!/usr/bin/env python
from securitycenter import SecurityCenter5
from datetime import datetime, timedelta
from email.mime.text import MIMEText
import smtplib


FROM_ADDRESS = 'no-reply@company.com'
TO = 'someone@company.com'
SC_HOSTNAME = '127.0.0.1'
SC_USERNAME = 'admin'
SC_PASSWORD = 'password'

class Object():
    pass

class SCObj(SecurityCenter5):
    def subscriptions(self):
        items = list()
        resp = self.get('feed').json()['response']

        # Now lets iterate through the information.  As long as the subscriptions
        # were activated at some point, then we will parse it.
        tf = {'true': True, 'false': False}
        for item in resp:
            obj = Object()
            if resp[item]['subscriptionStatus'] != 'Unconfigured':
                obj.name = item
                obj.updated = datetime.fromtimestamp(int(resp[item]['updateTime']))
                obj.status = resp[item]['subscriptionStatus']
                obj.stale = tf[resp[item]['stale']]
                items.append(obj)
        return items

    def scanner_statuses(self):
        statuses = {
            1:      {'title': 'Working',                'error': False},
            2:      {'title': 'Connection Error',       'error': True},
            4:      {'title': 'Connection Timeout',     'error': True},
            8:      {'title': 'Certificate Mismatch',   'error': True},
            16:     {'title': 'Protocol Error',         'error': True},
            32:     {'title': 'Authentication Error',   'error': True},
            64:     {'title': 'Invalid Configuration',  'error': True},
            128:    {'title': 'Reloading Scanner',      'error': False},
            256:    {'title': 'Plugins out of Sync',    'error': True},
            1024:   {'title': 'Updating Plugins',       'error': False},
            8192:   {'title': 'Updating Status',        'error': False},
            16384:  {'title': 'User Disabled',          'error': False},
            32768:  {'title': 'Requires Upgrade',       'error': True},
            131072: {'title': 'License Invalid',        'error': True},
        }
        scanners = list()
        resp = self.get('scanner', 
            params={'fields': 'name,ip,uptime,version,type,status'}).json()['response']
        for scanner in resp:
            obj = Object()
            obj.name = scanner['name']
            obj.address = scanner['ip']
            obj.status = statuses[int(scanner['status'])]['title']
            obj.version = scanner['version']
            obj.uptime = int(scanner['uptime'])
            obj.errored = statuses[int(scanner['status'])]['error']
            scanners.append(obj)
        return scanners


def send_email():
    issue = False

    # logging into the SecurityCenter install
    sc = SCObj(SC_HOSTNAME)
    sc.login(SC_USERNAME, SC_PASSWORD)

    # Lets get the data
    feeds = sc.subscriptions()
    scanners = sc.scanner_statuses()

    # now lets check to see if we have any issues...
    bad_scanners = [s for s in scanners if s.errored]
    bad_feeds = [f for f in feeds if (datetime.now() - f.updated).hours > 24]

    # and fire off the email if an issue exists
    if len(bad_feeds) > 0 or len(bad_scanners) > 0:
        msg = MIMEText('\n'.join([
            'You are being alerted to the fact that there may be an issue with'
            'your SecurityCenter installation.  The following issues have been'
            'discovered:'
            ''
            'Feed Issues:'
            ''
            '\n'.join(['* %s - %s'] % (s.name, s.updated) for s in bad_feeds])
            ''
            'Scanner Issues:'
            ''
            '\n'.join(['* %s [%s] %s' % (s.name, s.status, s.version) for s in bad_scanners])
        ]))
        msg['Subject'] = 'SecurityCenter Infrastructure Status Issue'
        msg['From'] = FROM_ADDRESS
        msg['To'] = TO_ADDRESS

        smtp = smtplib.SMTP('localhost')
        smtp.sendmail(msg['From'], [msg['To']], msg.as_string())


if __name__ == '__main__':
    send_email()