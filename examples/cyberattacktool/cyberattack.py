#!/usr/bin/env python
# This script is an ettempt to follow the TenableCyberAttackTool rev2
# document and build the dataset as needed.  This is by no means to be
# considered a finished product and is at best a proof of concept.  If this
# concept does work, then the script will be fleshed out and documented as
# is needed for general consumption.
#
# Author: Steven McGrath

from securitycenter import SCBase
from ConfigParser import ConfigParser
import re
import sys
import json

# First thing, we need to get the configuration file...
config = ConfigParser()
config.read('cyberattacktool.conf')


# Then we log into security center using the creds in the config file.
sc = SCBase(config.get('Security Center', 'username'),
            config.get('Security Center', 'password'),
            config.get('Security Center', 'host'),
            port=config.getint('Security Center', 'port'))


# A query function to make pulling data a bit less cumbersome.  I should
# really clean this up and use this as a starting point to build up
# pySecurityCenter to where it should be.
def query(tool, **args):
    api_count = 0
    dataset = []
    items = []
    opts = {}
    filters = []
    
    # This is the variable that determins how many records at a time we will
    # ask the API to send us at a time.  As this is defined in the confif file
    # there isnt much to say here, but from what I have seen, smaller numbers
    # are typically better (<10,000)
    increm = config.getint('Security Center', 'request_size')
    
    # This is how we were able to compact the wordy filter dictionaries
    # to simply item=value.  Here we are expanting that to what the
    # Security Center API expects it to be.
    for arg in args:
        filters.append({
            'filterName': arg,
            'operator': '=',
            'value': args[arg]
        })
    
    # We need to populate the opts dictionary with all of the needed
    # options for us to query the API.
    opts['tool'] = tool
    opts['sourceType'] = 'cumulative'
    opts['filters'] = filters
    
    # Here we will loop through requesting data from Security Center until
    # we have all of the available data for the query.
    while len(items) == increm or api_count == 0:
        opts['startOffset'] = api_count
        opts['endOffset'] = api_count + increm
        
        response = sc.vuln_search(**opts)
        items = response['response']['results']
        
        # We are handling this like this so that we don't get stuck into an
        # infinite loop if there are no results from the query
        if response['response']['totalRecords'] == '0':
            api_count += 1
        else:
            api_count += len(items)
        
        # Lets flatten the data a bit.  There is no reason the user should
        # to parse though a list of lists when there isnt any need for it.  So
        # we will add every item from the query into a single level list with
        # all of the results.
        for item in items:
            dataset.append(item)
        print_now('.')
    return dataset


# This function will build a dictionary that contains all of the plugins for
# each IP.
def build_ip_table(vulns, pre_load={}):
    for vuln in vulns:
        pre_load = insert_vuln(vuln, pre_load)
    return pre_load


# Build a dictionary of all of the destnation ports for each IP.
def build_port_table(vulns, pre_load={}):
    for vuln in vulns:
        if vuln['ip'] not in pre_load:
            pre_load[vuln['ip']] = []
        pre_load[vuln['ip']].append(int(vuln['port']))
    return pre_load


# Very simple, just build a list of unique IPs from the vulnerability data.
def build_ip_list(vulns, pre_load=[]):
    for vuln in vulns:
        if vuln['ip'] not in pre_load:
            pre_load.append(vuln['ip'])
    return list(set(pre_load))


# A simple function in order to keep with DRY principles.  We will check to
# see if the vulnerability is supposed to be suppressed and insert it into
# the ip dictionary (dataset) if it isn't supposed to be suppressed.
def insert_vuln(vuln, dataset):
    ignore_ids = config.get('Settings', 'ignore_ids').split()
    if vuln['pluginID'] not in ignore_ids:
        if vuln['ip'] not in dataset:
            dataset[vuln['ip']] = []
        dataset[vuln['ip']].append({
            'id': int(vuln['pluginID']),
            'port': int(vuln['port']),
            'name': vuln['pluginName']
        })
    return dataset


# This function allows us to compact several queries for plugin 90000 from the
# TCAT-rev2 document.  What we are doing is trying to pull out all server-
# related plugins and add them to a ip dictionary.
def build_expl_svc_table(vulns, pre_load={}):
    for vuln in vulns:
        if '(remote check)' in vuln['pluginName']:
            pre_load = insert_vuln(vuln, pre_load)
        if '(uncredentialed check)' in vuln['pluginName']:
            pre_load = insert_vuln(vuln, pre_load)
        # Commented all of this out until we figure out whats going on and why
        # I am getting client-data in the services table. >.<
        # UPDATE: this ended up being due to the client table and services
        #         table merging.  Ended up fixing this elsewhere.  These
        #         should be re-enabled to reduce the number of queries to the
        #         SC instance.
        #if vuln['port'] not in ['0','139','445']:
        #    pre_load = insert_vuln(vuln, pre_load)
        #if vuln['port'] in ['0','139','445']:
        #    if 'AC:L' in vuln['pluginText']:
        #        print vuln['pluginName']
        #        pre_load = insert_vuln(vuln, pre_load)
    return pre_load


# Here we will be parsing the data from PVS plugin 3 and attempt to build
# a simplistic model of the servers, clients, and the connection trusts
# between the two.
def build_con_lists(vulns, servers={}, clients={}, trusts=[]):
    recon = re.compile(r'(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})*\s->*\s(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}):(\d{1,5})')
    for vuln in vulns:
        if '0.0.0.0' in vuln['pluginText']:
            continue
        result = recon.findall(vuln['pluginText'])[0]
        trusts.append({'source': result[0],
                       'dest': result[1],
                       'port': int(result[2]),
                      })
        if result[1] not in servers:
            servers[result[1]] = []
        if result[0] not in clients:
            clients[result[0]] = []
        clients[result[0]].append(result[1])
        servers[result[1]].append(result[0])
    
    # We need to deduplicate the servers & clients...
    for server in servers:
        servers[server] = list(set(servers[server]))
    for client in clients:
        clients[client] = list(set(clients[client]))
    write_json(servers, 'servers.json')
    write_json(clients, 'clients.json')
    write_json(list(set(trusts)), 'trusts.json')
    return clients, servers, list(set(trusts))


# Exploit Chain Attack function
def chain_attack(address):
    paths = {}
    


# A simple function to dump a json file with the information in the dictionary
def write_json(data, filename):
    if config.getboolean('Settings', 'debug'):
        fobj = open(filename, 'w')
        fobj.write(json.dumps(data, sort_keys=True, indent=4))
        fobj.close()


def print_now(msg):
    if config.getboolean('Settings', 'debug'):
        sys.stdout.write(msg)
        sys.stdout.flush()


#### SECURITY CENTER QUERIES

print_now('Querying SC for Internet Remote Exploit IPs')
internetRemoteExploitIPs = build_ip_table(
                            query('vulndetails', 
                                  pluginText='External Access :', 
                                  exploitAvailable='true', 
                                  pluginType='passive'))


print_now('\nQuerying SC for Internet Report Ports')

internetRemotePorts = build_port_table(
                            query('vulndetails', 
                                  pluginID=14, 
                                  pluginType='passive'))


print_now('\nQuerying SC for Active Client IP List')
activeClientIPList = build_ip_list(
                        query('sumip', 
                              pluginID=3, 
                              pluginType='passive',
                              pluginText='0.0.0.0'))
activeClientIPList = build_ip_list(query('sumip', familyID='1000029'),
                                   activeClientIPList) # Mobile Devices
activeClientIPList = build_ip_list(query('sumip', familyID='1000016'), 
                                   activeClientIPList) # SMTP Clients
activeClientIPList = build_ip_list(query('sumip', familyID='1000027'), 
                                   activeClientIPList) # FTP Clients
activeClientIPList = build_ip_list(query('sumip', familyID='1000009'), 
                                   activeClientIPList) # Internet Messengers
activeClientIPList = build_ip_list(query('sumip', familyID='1000010'), 
                                   activeClientIPList) # IRC Clients


print_now('\nQuerying SC for Exploitable Client IP List')
exploitableClientIPList = build_ip_table(
                            query('vulndetails', 
                                  port='0',
                                  pluginType='passive',
                                  exploitAvailable='true'), {})
                            # must be some odd bug, but if I don't explicitly
                            # set an empty dictionary here,
                            # exploitableClientIPList and
                            # internetRemoteExploitIPs get merged.
exploitableClientIPList = build_ip_table(
                            query('vulndetails',
                                  port='0,139,445',
                                  pluginType='active',
                                  exploitAvailable='true',
                                  pluginText='AC:H'),
                            exploitableClientIPList)
exploitableClientIPList = build_ip_table(
                            query('vulndetails',
                                  port='0,139,445',
                                  pluginType='active',
                                  exploitAvailable='true',
                                  pluginText='AC:M'),
                            exploitableClientIPList)


print_now('\nQuerying SC for Exploitable Services')
exploitableServices = build_expl_svc_table(
                        query('vulndetails', 
                              pluginType='active',
                              exploitAvailable='true'))
exploitableServices = build_ip_table(
                        query('vulndetails',
                              port='1-138',
                              pluginType='active',
                              exploitAvailable='true'),
                        exploitableServices)
exploitableServices = build_ip_table(
                        query('vulndetails',
                              port='140-144',
                              pluginType='active',
                              exploitAvailable='true'),
                        exploitableServices)
exploitableServices = build_ip_table(
                        query('vulndetails',
                              port='146-65535',
                              pluginType='active',
                              exploitAvailable='true'),
                        exploitableServices)
exploitableServices = build_ip_table(
                        query('vulndetails',
                              port='0,139,445',
                              pluginText='AC:L',
                              pluginType='active',
                              exploitAvailable='true'),
                        exploitableServices)


print_now('\nQuerying SC for Connection Lists')
connectedServers, sourceClients, trustPairs = build_con_lists(
                                                query('vulndetails',
                                                      pluginType='passive',
                                                      pluginID=3))


print_now('\n')
#### END SECURITY CENTER QUERIES


# Plugin 90000 - Exploitable services with have visibility from the internet
print_now('Running Correlation for 90000:\n')
for host in internetRemotePorts:
    if host in exploitableServices:
        for port in internetRemotePorts[host]:
            for svc in exploitableServices[host]:
                if svc['port'] == port:
                    print_now('.')
                    if host not in internetRemoteExploitIPs:
                        internetRemoteExploitIPs[host] = []
                    if svc not in internetRemoteExploitIPs[host]:
                        internetRemoteExploitIPs[host].append(svc)
write_json(internetRemoteExploitIPs, '90000.json')


# Plugin 90001 - Systems that connect to the internet and have exploitable
#                client software
print_now('\nRunning Correlation for 90001:\n')
internetClientExploitIPs = {}
for host in exploitableClientIPList:
    if host in activeClientIPList:
        print_now('.')
        internetClientExploitIPs[host] = exploitableClientIPList[host]
write_json(internetClientExploitIPs, '90001.json')


# Plugin 90002 - Systems that accept trust relationships from systems with
#                exploitable vulnerabilities
print_now('\nRunning Correlation for 90002:\n')
connectionTrustExploitIPs = {}
for server in connectedServers:
    add = False
    expl_trusts = {
        'inet_expl_servers': [],
        'inter_expl_servers': [],
        'inet_expl_clients': [],
        'inter_expl_clients': [],
    }
    clients = connectedServers[server]
    for client in clients:
        if client in internetRemoteExploitIPs:
            add = True
            expl_trusts['inet_expl_servers'].append(client)
        if client in exploitableServices:
            add = True
            expl_trusts['inter_expl_servers'].append(client)
        if client in exploitableClientIPList:
            add = True
            expl_trusts['inet_expl_clients'].append(client)
        if client in internetClientExploitIPs:
            add = True
            expl_trusts['inter_expl_clients'].append(client)
    if add:
        print_now('.')
        connectionTrustExploitIPs[server] = expl_trusts
write_json(connectionTrustExploitIPs, '90002.json')


# Plugin 90003 - Server exploit attack chain analysis
print_now('\nRunning Correlation for 90003:\n')
chainAttackIPList = {}
for host in internetRemoteExploitIPs:
    pass
write_json(chainAttackIPList, '90003.json')