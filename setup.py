from distutils.core import setup
import sys

if sys.version_info < (2, 6, 0):
    sys.stderr.write('pySecurityCenter requires Python 2.6 or newer.\n')
    sys.exit(-1)

if sys.version_info > (3, 0, 0):
    sys.stderr.write('pySecurityCenter is not compatable with Python 3.\n')

setup(
    name='pySecurityCenter',
    version='0.3.0a1',
    description='Security Center 4 API Module',
    author='Steven McGrath',
    author_email='smcgrath@tenable.com',
    url='https://github.com/SteveMcGrath/pySecurityCenter',
    py_modules=['securitycenter'],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Information Technology',
        'License :: OSI Approved :: GNU Lesser General Public License v2 (LGPLv2)',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Topic :: Software Development :: Libraries :: Application Frameworks',
    ]
)