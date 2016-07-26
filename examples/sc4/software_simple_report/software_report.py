import securitycenter

HOST = 'DNS_NAME_OR_IP'
USER = 'USERNAME'
PASS = 'PASSWORD'
CSV_FILENAME = 'example.csv'
IGNORE = [
# Some Example Ignores:
 'Security Update',
# 'Python',
]

sc = securitycenter.SecurityCenter4(HOST)
sc.login(USER, PASS)

software = {}
                                        # Remove the ): and uncomment the line
                                        # below to filter down based on an
                                        # asset list.  Just make sure to get the
                                        # ID of the asset list.
for item in sc.query('listsoftware'):   #,assetID=81):
    ignore_me = False
    name = item['name'].split('[')[0].strip()
    for iname in IGNORE:
        if iname in name:
            ignore_me = True
    if not ignore_me:
        if name not in software:
            print 'Added %s from %s' % (name, item['name'])
            software[name] = 0
        software[name] += int(item['count'])

with open(CSV_FILENAME, 'w') as outfile:
    outfile.write('"Software Item","Count"\n')
    for item in software:
        outfile.write('"%s","%s"\n' % (item, software[item]))