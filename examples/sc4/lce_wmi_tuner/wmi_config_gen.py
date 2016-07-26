#!/usr/bin/env python
import securitycenter
import os
from ConfigParser import ConfigParser

# Main configuration template
conf_tpl = '''
options = {
    log-directory {LOG_DIR}
    lce-server {LCE_HOST} {
        client-auth auth-secret-key {LCE_AUTH_KEY}
    }
    server-port {LCE_PORT}
    {SYSLOG_SERVERS}
    heartbeat-frequency {HEARTBEAT}
    statistics-frequency {STATISTICS}
    {DEBUG}
    {WMI_HOSTS}
}
'''

# WMI host configuration Template
wmi_tpl = '''
    WMI-host {
        address {WMI_ADDRESS}
        {DOMAIN}
        username {USERNAME}
        password {PASSWORD}
        monitor {MONITOR}
    }
'''

# First thing we need to do is open the config file.
conf = ConfigParser()
conf.read(os.path.join(os.path.dirname(__file__), 'wmi_config_gen.conf'))

# Then we will build the base config off of our own config file.
wmi = conf_tpl
wmi = wmi.replace('{LOG_DIR}', conf.get('LCE Settings', 'log_directory'))
wmi = wmi.replace('{LCE_HOST}', conf.get('LCE Settings', 'lce_server'))
wmi = wmi.replace('{LCE_AUTH_KEY}', conf.get('LCE Settings', 'lce_auth_key'))
wmi = wmi.replace('{LCE_PORT}', conf.get('LCE Settings', 'lce_server_port'))
wmi = wmi.replace('{HEARTBEAT}', conf.get('LCE Settings', 'heartbeat'))
wmi = wmi.replace('{STATISTICS}', conf.get('LCE Settings', 'stats'))

# Here we will parse out all of the sysog servers specified and add the needed
# entries for them into the wmi_monitor.conf template.
syslog_servers = conf.get('LCE Settings', 'syslog').split(',')
syslog_entries = []
for syslog in syslog_servers:
    syslog = syslog.strip()
    if syslog is not '':
        syslog_entries.append('syslog-server %s' % syslog)
wmi = wmi.replace('{SYSLOG_SERVERS}', '\n'.join(syslog_entries))

# Next we check to see if debug is turned on, if so, then we need to add that
# entry.
if conf.getboolean('LCE Settings', 'debug'):
    wmi = wmi.replace('{DEBUG}', 'debug')
else:
    wmi = wmi.replace('{DEBUG}', '')

# Now that we got all of the base configuration stuff out of the way, its time
# to poll Security Center for the IPs in the asset list that we have been told
# to talk to and build the wmi hosts based off of that.
sc4 = securitycenter.SecurityCenter4(conf.get('SC4 Settings', 'host'),
                                    port=conf.get('SC4 Settings', 'port'))
sc4.login(conf.get('SC4 Settings', 'user'), conf.get('SC4 Settings', 'pass'))

assets = sc4.assets()['response']['assets']

# Here we are querying SC4 for the IPs in the asset list then reformatting the
# information into a simple list.
ip_list = []
for asset in assets:
    if asset['name'] == conf.get('SC4 Settings', 'asset'):
        ip_list = sc4.vuln_search(tool='sumip', 
                                  startOffset=0, 
                                  endOffset=100000, 
                                  sourceType='cumulative', 
                                  filters=[{
                                        'filterName': 'assetID', 
                                        'value': 6, 
                                        'operator': '='
                                  }])['response']['results']

# This way didnt work so well.  SC4 liked to glob data together in a way we
# cant use without a lot of extra parsing.
#        for item in sc4.asset_get_ips(asset['id'])['response']['viewableIPs']:
#            for address in item['ipList'].split('\n'):
#                ip_list.append(address)

# A simple catch incase we get an empty dataset.
if len(ip_list) < 1:
    exit()

# And now for the magic.  We are going to build a template for each host we
# queried and then join them together into the config file.
hosts = []
for ip in ip_list:
    domain = ''
    host = wmi_tpl
    host = host.replace('{WMI_ADDRESS}', ip['ip'])
    host = host.replace('{USERNAME}', conf.get('WMI Settings', 'user'))
    host = host.replace('{PASSWORD}', conf.get('WMI Settings', 'pass'))
    host = host.replace('{MONITOR}', conf.get('WMI Settings', 'monitor'))
    if conf.get('WMI Settings', 'domain') != '':
        domain = 'domain %s' % conf.get('WMI Settings', 'domain')
    host = host.replace('{DOMAIN}', domain)
    hosts.append(host)
wmi = wmi.replace('{WMI_HOSTS}', '\n'.join(hosts))

# And lastly, we write the config to a file.
wmi_file = open('wmi_monitor.conf', 'w')
wmi_file.write(wmi)
wmi_file.close()