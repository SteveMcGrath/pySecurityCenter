from distutils.core import setup
import sys

# A simple little hack to generate the RST file for pretty formatting for pypi.
try:
    import pypandoc
    with open('README', 'w') as pypidoc:
        pypidoc.write(pypandoc.convert('README.md', 'rst'))
except:
    pass

# These are the requirements for pySecurityCenter
requirements = ['poster',]

# If we are running on something thats not 2.6 or 2.7, we will need the
# simplejson module.  Python versions less than 2.6 need specifically version
# 2.1.0 as newer ones break on python 2.4.  The reason we need simplejson on
# versions greater than 2.7 is that it seems like the typcasting on the json
# module in version 3.x is too strict, and is causing a lot of issues.
extra = {}
if sys.version_info < (2, 6, 0):
    requirements.append('simplejson==2.1.0')
if sys.version_info > (3,):
    requirements.append('simplejson')
    extra['use_2to3'] = True

setup(
    name='pySecurityCenter',
    version='0.3.8.4',
    description='Security Center 4 API Module',
    author='Steven McGrath',
    author_email='smcgrath@tenable.com',
    url='https://github.com/SteveMcGrath/pySecurityCenter',
    py_modules=['securitycenter'],
    install_requires=requirements,
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Information Technology',
        'License :: OSI Approved :: GNU Lesser General Public License v2 (LGPLv2)',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2.4',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Topic :: Software Development :: Libraries :: Application Frameworks',
    ],
    **extra
)
