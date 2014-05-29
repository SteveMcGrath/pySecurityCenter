#!/usr/bin/env python
from securitycenter.v1 import SecurityCenter
import time

# NOTE: all time is based on Unix time. 86400 is 1 day in seconds.

update_list = [{
    'asset_id': 28,
    'filters': {
        'sensor': 'HomeNet_Snort',
        'endtime': int(time.time()),
        'starttime': (int(time.time()) - 86400),
        },
    },{
    'asset_id': 29,
    'filters': {
        'type': 'nbs',
        'endtime': int(time.time()),
        'starttime': (int(time.time()) - 86400),
        },
    },
]

host = 'HOST'
username = 'api_user'
password = 's3cr3tp@ssw0rd'

sc = SecurityCenter(host, username, password)

for update in update_list:
    events = sc.query('sumip', source='lce', **update['filters'])
    ips = []
    for event in events:
        ips.append(event['address'])
    sc.asset_update(update['asset_id'], ips=ips)
