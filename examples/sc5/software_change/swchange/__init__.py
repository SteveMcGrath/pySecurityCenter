from . import models
from . import population
from . import reporter
from securitycenter import SecurityCenter5 as SecurityCenter
from ConfigParser import ConfigParser
from base64 import b64encode, b64decode
import os, sys, getpass, getopt


def main():
    configfile = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'config.conf')
    config = ConfigParser()
    populate = False
    report = False

    try:
        opts, args = getopt.getopt(sys.argv[1:],"pr",["populate","report"])
    except getopt.GetoptError:
        print 'reporter.py -p -r'
        sys.exit(2)
    for opt, arg in opts:
        if opt in ('-p', '--populate'):
            populate = True
        elif opt in ('-r', '--report'):
            report = True

    if not os.path.exists(configfile):
        s = models.Session()
        # Well there wasn't a config file located along side the downloader
        # script, so we should create a new one.
        config.add_section('SecurityCenter')
        config.set('SecurityCenter', 'host', raw_input('SecurityCenter Address : '))
        config.set('SecurityCenter', 'user', raw_input('SecurityCenter Username : '))
        config.set('SecurityCenter', 'pass', b64encode(getpass.getpass('SecurityCenter Password : ')))
        config.set('SecurityCenter', 'expire', raw_input('Expiration Threshhold (in days) : '))
        config.set('SecurityCenter', 'path', raw_input('Folder to place reports : '))
        marker = True
        assets = []
        while marker:
            aid = raw_input('Asset List ID to Restrict to : ')
            rname = raw_input('Report Name? : ')
            if aid is not '' and rname is not '':
                s.add(models.AssetList(id=int(aid), name=rname))
                assets.append(aid)
            else:
                marker = False
        config.set('SecurityCenter', 'asset_ids', ','.join(assets))
        s.commit()
        s.close()
        with open(configfile, 'wb') as fobj:
            config.write(fobj)
    else:
        config.read(configfile)

    if populate:
        sc = SecurityCenter(config.get('SecurityCenter', 'host'))
        sc.login(config.get('SecurityCenter', 'user'),
                 b64decode(config.get('SecurityCenter', 'pass')))
        for asset_id in config.get('SecurityCenter', 'asset_ids').split(','):
            population.gen(sc, int(asset_id), config.getint('SecurityCenter', 'expire'))
    if report:
        for asset_id in config.get('SecurityCenter', 'asset_ids').split(','):
            reporter.generate_html_report(config.get('SecurityCenter', 'path'), int(asset_id))

