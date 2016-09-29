from securitycenter import SecurityCenter5
from datetime import date
from time import mktime
from pygal.style import BlueStyle
from pygal import DateLine
from sys import stdout

username = 'USER'
password = 'PASS'
address = 'HOST'
results = [True,True]
start_boundry = date(2015,1,1)
end_boundry = date(2016,12,31)
data = {}

sc = SecurityCenter5(address)
sc.login(username, password)

offset = 0
done = False
while len(results) > 0 or done:
    print '\nPulling plugins from %s to %s' % (offset, offset + 10000)
    results = sc.get('plugin', params={
        'fields': 'pluginPubDate,modifiedTime',
        'size': 1000,
        'startOffset': offset,
        'endOffset': offset + 10000,
    }).json()['response']

    for item in results:
        stdout.write('\rProcessing Plugin %s of %s' % (results.index(item) + 1, len(results)))
        stdout.flush()
        try:
            d = date.fromtimestamp(int(item['pluginPubDate']))
            m = date.fromtimestamp(int(item['modifiedTime']))
        except:
            pass
        else:
            if d > start_boundry and d < end_boundry:
                if d not in data:
                    data[d] = 0
                data[d] += 1
    offset += 10000

chart = DateLine(
    style=BlueStyle,
    show_dots=False,
    fill=True,
)
chart.add('Plugins', sorted([(x, data[x]) for x in data], key=lambda tup: tup[0]))
chart.render_in_browser()
