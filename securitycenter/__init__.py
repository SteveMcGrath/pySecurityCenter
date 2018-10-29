from .sc4 import SecurityCenter4
from .sc5 import SecurityCenter5
from .nessus import Nessus
from .pvs import PVS
import warnings

warnings.warn('pySecurityCenter has been deprecated in favor of pyTenable', 
    DeprecationWarning)

__author__ = 'Steven McGrath <steve@chigeek.com>'
__version__ = '3.1.2'
__url__ = 'https://github.com/SteveMcGrath/pySecurityCenter'
__description__ = 'Python Interface into Tenable\'s SecurityCenter'
