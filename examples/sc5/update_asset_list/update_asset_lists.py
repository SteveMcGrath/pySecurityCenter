import securitycenter
import getpass
import csv
import os


def import_csv_file(filename, sc):
    with open(filename) as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            sc.patch('asset/%s' % row['asset_id'], json={
                'definedIPs': row['addresses'],
            })
            print '** Updated %s using %s' % (row['asset_id'], row['addresses'])


if __name__ == '__main__':
    csvfile = raw_input('CSV Batch File Path : ')
    if not os.path.exists(csvfile):
        print '!!! CSV file does not exist!  Aborting. !!!'
        exit()
    host = raw_input('SecurityCenter Server : ')
    username = raw_input('SecurityCenter Username : ')
    password = getpass.getpass('SecurityCenter Password : ')
    sc = securitycenter.SecurityCenter5(host)
    sc.login(username, password)
    import_csv_file(csvfile, sc)