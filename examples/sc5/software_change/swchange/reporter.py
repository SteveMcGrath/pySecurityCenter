from jinja2 import Environment, PackageLoader
from .models import Session, Host, Entry, AssetList
from datetime import datetime
import os


def generate_html_report(base_path, asset_id):
    '''
    Generates the HTML report and dumps it into the specified filename
    '''
    jenv = Environment(loader=PackageLoader('swchange', 'templates'))
    s = Session()
    #hosts = s.query(Host).filter_by(asset_id=asset_id).all()
    asset = s.query(AssetList).filter_by(id=asset_id).first()
    if not asset:
        print 'Invalid Asset ID (%s)!' % asset_id
        return
    filename = os.path.join(base_path, '%s-INV-CHANGE-%s.html' % (
        asset.name,
        datetime.now().strftime('%Y-%m-%d.%H.%M.%S'))
    )
    print 'Generating Report : %s' % filename
    with open(filename, 'wb') as report:
        report.write(jenv.get_template('layout.html').render(
            asset=asset,
            current_date=datetime.now()
        ))
