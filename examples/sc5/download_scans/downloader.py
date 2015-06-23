#!/usr/bin/env python
from securitycenter import SecurityCenter5
from datetime import date, datetime, timedelta
from StringIO import StringIO
from zipfile import ZipFile
from base64 import b64encode, b64decode
import logging, os


# Setup the logging facility.
logger = logging.getLogger('SCAN_RESULT_DOWNLOAD')
logger.setLevel(logging.DEBUG)


def download_scans(sc, age=0, unzip=False, path='scans'):
    '''Scan Downloader
    Here we will attempt to download all of the scans that have completed between
    now and AGE days ago.

    sc = SecurityCenter5 object
    age = how many days back do we want to pull? (default: 0)
    unzip = Do we want to uncompress the nessus files? (default: False)
    path = Path where the resulting data will be placed. (default: scans)
    '''

    # if the download path doesn't exist, we need to create it.
    if not os.path.exists(path):
        logger.debug('scan path didn\'t exist. creating it.')
        os.makedirs(path)

    # Now we will need to comuter the timestamp for the date that the age has
    # apecified.  The API expects this in a unix timestamp format.
    findate = (date.today() - timedelta(days=age))

    # Lets get the list of scans that had completed within the timefram that we
    # had specified.
    logger.debug('getting scan results for parsing')
    resp = sc.get('scanResult', params={
        'startTime': findate.strftime('%s'),
        'fields': 'name,finishTime,downloadAvailable,repository',
    })

    for scan in resp.json()['response']['usable']:
        # If this particular scan does not have any results (either it was a 
        # partial, failed, or incomplete scan) then we have nothing further to
        # do and should simply ignore this scan.
        if scan['downloadAvailable'] == 'false':
            logger.debug('%s/"%s" not available for download' % (scan['id'], 
                                                                    scan['name']))
        else:
            # Well look, this scan actually has results, lets go ahead and pull
            # them down.
            logger.debug('%s/"%s" downloading' % (scan['id'], scan['name']))
            scandata = sc.post('scanResult/%s/download' % scan['id'], 
                              json={'downloadType': 'v2'})
            sfin = datetime.fromtimestamp(int(scan['finishTime']))

            # The filename is being computed generically here.  As this will be
            # used whether we extract the .nessus file out of the zipfile or
            # not.
            filename = '%s-%s.%s.%s' % (scan['id'], 
                                        scan['name'].replace(' ', '_'), 
                                        scan['repository']['id'],
                                        sfin.strftime('%Y.%m.%d-%H.%M'))
            if unzip:
                # Unzip that .nessus file!
                logger.debug('extracting %s/%s' % (scan['id'], scan['name']))
                zfile = ZipFile(StringIO(buf=scandata.content))
                scanfile = zfile.filelist[0]
                scanfile.filename = '%s.nessus' % filename
                zfile.extract(scanfile, path=path)
            else:
                # We want to keep it compressed, just dump to disk.
                logger.debug('writing zip for %s/%s' % (scan['id'], scan['name']))
                with open('%s.zip' % filename, 'wb') as zfile:
                    zfile.write(scandata.content)

            # Were done with this scan file!!!
            logger.info('%s/"%s" downloaded' % (scan['id'], scan['name']))


if __name__ == '__main__':
    from ConfigParser import ConfigParser
    import getpass

    # Lets setup the config parser.
    configfile = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'config.conf')
    config = ConfigParser()

    if not os.path.exists(configfile):
        # Well there wasn't a config file located along side the downloader
        # script, so we should create a new one.
        config.add_section('SecurityCenter')
        config.set('SecurityCenter', 'host', raw_input('SecurityCenter Address : '))
        config.set('SecurityCenter', 'user', raw_input('SecurityCenter Username : '))
        config.set('SecurityCenter', 'pass', b64encode(getpass.getpass('SecurityCenter Password : ')))
        config.add_section('ScanResults')
        config.set('ScanResults', 'age', raw_input('Scan Age (in Days) : '))
        config.set('ScanResults', 'path', raw_input('Scan Download Path : '))
        config.set('ScanResults', 'unzip', raw_input('Extract the .Nessus Files? (yes/no) : '))
        config.add_section('Logging')
        config.set('Logging', 'level', 'info')
        with open(configfile, 'wb') as fobj:
            config.write(fobj)
    else:
        config.read(configfile)

    # We need to translate the logging levels from the string thats in the
    # config file to something that the logging module understands.
    log_levels = {
        'debug': logging.DEBUG,
        'info': logging.INFO,
        'warn': logging.WARN,
        'error': logging.ERROR,
    }

    # Lets setup the logging file handler so that we can actually output a log
    # file.
    fh = logging.FileHandler('scan_downloads.log')
    fh.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
    fh.setLevel(log_levels[config.get('Logging', 'level')])
    logger.addHandler(fh)

    # Now lets actually connect to the SecurityCenter instance and then pass the
    # sc object off to the scan downloader function.
    sc = SecurityCenter5(config.get('SecurityCenter', 'host'))
    sc.login(config.get('SecurityCenter', 'user'), 
             b64decode(config.get('SecurityCenter', 'pass')))
    download_scans(sc, 
        age=config.getint('ScanResults', 'age'),
        unzip=config.getboolean('ScanResults', 'unzip'),
        path=config.get('ScanResults', 'path')
    )