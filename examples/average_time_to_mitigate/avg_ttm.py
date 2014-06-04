import securitycenter

HOST = 'HOSTNAME or IP_ADDRESS'
USER = 'USERNAME'
PASS = 'PASSWORD'
ASSET_ID = 81

def get_ttm(**filters):
    sc = securitycenter.SecurityCenter(HOST, USER, PASS)
    data = sc.query('vulndetails', source='patched', **filters)
    agg = 0
    for item in data:
        agg += int(item['lastSeen']) - int(item['firstSeen'])
    avg = float(agg) / len(data)
    print 'Average Hours to Mitigate : %d' % int(avg / 3600)
    print 'Average Days to Mitigate : %s' % int(avg / 3600 / 24)

if __name__ == '__main__':
    get_ttm(assetID=ASSET_ID, severity='4,3,2,1')