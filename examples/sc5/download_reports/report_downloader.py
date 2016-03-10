#!/usr/bin/env python
from securitycenter import SecurityCenter5
from datetime import date, datetime, timedelta
import logging, os


# Setup the logging facility.
logger = logging.getLogger('REPORT_DOWNLOAD')
logger.setLevel(logging.DEBUG)

def download(sc, age=0, path='reports', **args):
    '''Report Downloader
    The report downloader will pull reports down from SecurityCenter
    based on the conditions provided to the path provided.

    sc =        SecurityCenter5 object
    age =       number of days old the report may be to be included in the
                search.
    path =      The path to the download folder.  One will be created if
                it doesn't exist.

    OPTIONAL ARGUMENTS:

    type =      Specifies the type of the report.  e.g. pdf, csv, etc.
    name =      A subset of the name of the report used for pattern matching.
    '''

    # if the download path doesn't exist, we need to create it.
    if not os.path.exists(path):
        logger.debug('report path didn\'t exist. creating it.')
        os.makedirs(path)

    # Now we will need to comuter the timestamp for the date that the age has
    # apecified.  The API expects this in a unix timestamp format.
    findate = (date.today() - timedelta(days=age))

    # Lets get the listing of reports that we will be working with...
    reports = sc.get('report', params={
        'startTime': findate.strftime('%s'),
        'fields': 'name,type,status,finishTime'
    })

    # now we will work our way through the resulting dataset and attempt
    # to download the reports if they meet our criteria.
    for report in reports.json()['response']['usable']:

        # We can only download completed reports, so we have no reason
        # to even try to download anything that isnt in the completed
        # status.
        if report['status'] == 'Completed':

            # If the name or type arguments are passed, then we will
            # want to make sure that we only download the relevent
            # reports that match these criteria.  For name, we will
            # be performing a simple pattern match, and for type we will
            # check the report type.  e.g. pdf, csv, etc.
            if 'name' in args and args['name'] not in report['name']:
                continue
            if 'type' in args and args['type'].lower() != report['type'].lower():
                continue

            # now to actually get the report...
            report_data = sc.post('report/%s/download' % report['id'],
                json={'id': int(report['id'])})

            # compute a report name...
            report_name = '%s-%s.%s' % (
                report['name'].replace(' ', '_'),
                report['finishTime'],
                report['type']
            )

            # and finally write the report to disk...
            logger.info('writing %s to disk' % report_name)
            with open(os.path.join(path, report_name), 'wb') as report_file:
                report_file.write(report_data.content)


if __name__ == '__main__':
    from ConfigParser import ConfigParser
    from base64 import b64encode, b64decode
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
        config.add_section('Reports')
        config.set('Reports', 'age', raw_input('Report Age (in Days) : '))
        config.set('Reports', 'path', raw_input('Report Download Path : '))
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
    fh = logging.FileHandler('report_downloads.log')
    fh.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
    fh.setLevel(log_levels[config.get('Logging', 'level')])
    logger.addHandler(fh)

    # Now lets actually connect to the SecurityCenter instance and then pass the
    # sc object off to the report downloader function.
    sc = SecurityCenter5(config.get('SecurityCenter', 'host'))
    sc.login(config.get('SecurityCenter', 'user'),
             b64decode(config.get('SecurityCenter', 'pass')))
    download(sc,
        age=config.getint('Reports', 'age'),
        path=config.get('Reports', 'path')
    )
