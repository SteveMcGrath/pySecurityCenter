import securitycenter
import getpass


def get_info(sc):
    data = {}

    # What we will be doing here is getting the list of usable asset lists that
    # user has access to, then iterating through each asset list to get the
    # viewable IPs from SecurityCenter.  We will then be re-parsing that data
    # into something a little more usable.
    for asset_list in sc.get('asset').json()['response']['usable']:
        resp = sc.get('asset/%s' % asset_list['id'], params={'fields': 'name,viewableIPs'})
        ips = {}  
        for item in resp.json()['response']['viewableIPs']:
            # This is where we work to convert the pipe and newline delimited
            # format of the data that SecurityCenter uses to a list of tuples
            repo = item['repository']['name']
            ips[repo] = []
            for line in item['ipList'].split('\n'):
                ips[repo].append(line.split('|'))

        # Dump all of the information into the base data dictionary.
        data[resp.json()['response']['id']] = {
            'name': resp.json()['response']['name'],
            'ips': ips,
        }

    # Return the dictionary to the calling function.
    return data


if __name__ == '__main__':
    # Get the needed login info from the user...
    host = raw_input('SecurityCenter Server : ')
    username = raw_input('SecurityCenter Username : ')
    password = getpass.getpass('SecurityCenter Password : ')
    
    # Log into the SecurityCenter environment and get the parsed data back...
    sc = securitycenter.SecurityCenter5(host)
    sc.login(username, password)
    asset_lists = get_info(sc)

    # now to take the data we got and to display it.  The display used here is
    # most definately not efficient, however its used mearly to display the data
    for item in asset_lists:
        print '-=[%s | %s]=-' % (item, asset_lists[item]['name'])
        for repo in asset_lists[item]['ips']:
            print 'REPOSITORY: %s' % repo
            for ip in asset_lists[item]['ips'][repo]:
                print '\t%s' % '/'.join(ip)