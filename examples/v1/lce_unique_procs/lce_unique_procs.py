from securitycenter.v1 import SecurityCenter
import time
import re

username = 'USERNAME'
password = 'PASSWORD'
hostname = 'HOSTNAME'
days = 7

sc = SecurityCenter(hostname, username, password)

queries = [{
    'eventName': 'Unique_Windows_Executable',
    'regex': re.compile(r'invoked \'(.*?)\''),
    'regex_type': 'single',
    },{
    'eventName': 'Daily_Command_Summary',
    'regex': re.compile(r'day: (.*?) \('),
    'regex_type': 'multiple',
    }
]

procs = set()

for query in queries:
    data = sc.query('syslog', source='lce',
                    eventName=query['eventName'],
                    endtime=int(time.time()),
                    starttime=(int(time.time()) - (86400 * days))
                   )
    for item in data:
        values = query['regex'].findall(item['message'])
        for value in values:
            if query['regex_type'] == 'single':
                procs.add(value)
            if query['regex_type'] == 'multiple':
                for val in value.split(', '):
                    procs.add(val)
print '%s:\t%s' % (len(procs), ', '.join(procs))
