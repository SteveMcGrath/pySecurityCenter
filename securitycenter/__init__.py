from sc4 import SecurityCenter4 as SecurityCenter
from sc4 import SecurityCenter4
from sc5 import SecurityCenter5
from nessus import Nessus
# as the orm doesnt support versions of python earlier than 2.6, lets not
# implicitly import the whole thing and instead make the dev explicity pull it
# in.
#import orm import SecurityCenterClient

__authors__ = [
    'Steven McGrath <steve@chigeek.com>', 
    'David Lord <davidism@gmail.com>',
]
__version__ = '2.1.6'
__url__ = 'https://github.com/SteveMcGrath/pySecurityCenter'
__description__ = 'Python Interface into Tenable\'s SecurityCenter'