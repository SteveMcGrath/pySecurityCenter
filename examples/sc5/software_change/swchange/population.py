import re, datetime, json, sys
from .models import Session, Host, Entry

def gen(sc, asset, expire):
    '''
    Database population function.

    What we are doing here is trying to interpret the output of plugin ID 20811
    and use that information to help populate the database with individualized
    entries of the software that is installed on the host.  This information will
    later be used to build the report.
    '''

    # The following regex patters are used to pull out the needed fields from
    # Plugin ID 20811
    redate = re.compile(r'\[installed on (\d{4})/(\d{1,2})/(\d{1,2})\]')
    reinvdate = re.compile(r'\[installed on (\d{1,2})/(\d{1,2})/(\d{4})\]')
    rever = re.compile(r'\[version (.*?)\]')
    resw = re.compile(r'^([\w\s\.\(\-\)\+]*)')
    s = Session()
    ts = datetime.datetime.now()
    for vuln in sc.analysis(('pluginID','=','20811,22869'), 
                            ('asset', '=', {'id': str(asset)}),
                            tool='vulndetails'):


        # First we need to get the host information...
        nh = False
        host = s.query(Host).filter_by(ip=vuln['ip']).first()
        if not host:
            host = Host()
            nh = True
        hdata = sc.analysis(('ip', '=', vuln['ip']),tool='sumip')[0]
        host.ip = vuln['ip']
        host.name = vuln['netbiosName']
        host.cpe = hdata['osCPE']
        host.dns = hdata['dnsName']
        host.asset_id = asset
        if nh:
            s.add(host)
        else:
            s.merge(host)
        s.commit()
        sys.stdout.write('%4d\t%-16s\t%-40s' % (host.id, host.ip, host.dns))
        sys.stdout.flush()

        if vuln['pluginID'] == '22869':
            if 'CentOS Linux system' in vuln['pluginText'] or 'Red Hat Linux system' in vuln['pluginText']:
                software = re.findall('  ([a-zA-Z0-9\.\-]*)\|',vuln['pluginText'])
                for item in software:
                    entry = Entry()
                    entry.name = item
                    entry.timestamp = ts
                    entry.host_id = host.id
                    s.add(entry)
                    s.commit()
            elif 'SunOS 5.10' in vuln['pluginText']:
                software = re.findall('Patch: ([^ ]*)', vuln['pluginText'])
                for item in software:
                    entry = Entry()
                    entry.name = item
                    entry.timestamp = ts
                    entry.host_id = host.id  
                    s.add(entry)
                    s.commit()
            elif 'Solaris 11 system' in vuln['pluginText']:
                software = re.findall('([\w\/]+)\W+([0-9\.\-]+).*\n',vuln['pluginText'])
                for item in software:
                    entry = Entry()
                    entry.name = item[0]
                    entry.version = item[1]
                    entry.timestamp = ts
                    entry.host_id = host.id
                    s.add(entry)  
                    s.commit()  
            elif 'Mac OS X system' in vuln['pluginText']:
                software = re.findall('  ([a-zA-Z0-9\.\-\_]*\.pkg)\n',vuln['pluginText'])
                for item in software:
                    entry = Entry()
                    entry.name = item
                    entry.timestamp = ts
                    entry.host_id = host.id
                    s.add(entry)  
                    s.commit()   
            else:
                sys.stdout.write('\t[NO FORMATTER]')
                sys.stdout.flush()

        if vuln['pluginID'] == '20811':
            software = False
            patches = False
            sw = None
            nh = False
            s.commit()
            for line in vuln['pluginText'].split('\n'):
                if '</plugin_output>' in line:
                    continue
                if line == u'The following software are installed on the remote host :':
                    software = True
                    patches = False
                    continue
                if line == u'The following updates are installed :':
                    patches = True
                    continue

                if software and line != '':
                    names = resw.findall(line)
                    vers = rever.findall(line)
                    dates = redate.findall(line)
                    new = Entry()
                    if len(names) > 0: new.name = names[0].strip()
                    if len(vers) > 0: new.version = vers[0]
                    try:
                        if len(dates) > 0:
                            date = datetime.date(year=int(dates[0][0]), 
                                                 month=int(dates[0][1]),
                                                 day=int(dates[0][2]))
                            new.date = date
                        else:
                            dates = reinvdate.findall(line)
                            if len(dates) > 0:
                                date = datetime.date(year=int(dates[0][2]), 
                                                     month=int(dates[0][0]),
                                                     day=int(dates[0][1]))
                                new.date = date                        
                    except:
                        pass
                    if patches:
                        if line[:2] != '  ':
                            sw = line.strip(':').strip()
                            continue
                        else:
                            new.name = '%s (%s)' % (new.name, sw)

                    new.timestamp = ts
                    new.host_id = host.id
                    s.add(new)
        s.commit()
        sys.stdout.write('\tdone\n')
        sys.stdout.flush()
    s.commit()

    # Now to expire the old data out...
    exp = datetime.datetime.now() - datetime.timedelta(days=expire)
    print exp

    # First to delete the aged out entries
    for entry in s.query(Entry).filter(Entry.timestamp < exp).all():
        s.delete(entry)
    s.commit()

    # Next to delete any hosts that we arent pulling info for anymore...
    for host in s.query(Host).all():
        if len(host.entries) == 0:
            s.delete(host)
    s.commit()
    s.close()