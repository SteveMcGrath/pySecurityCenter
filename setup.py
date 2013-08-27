from setuptools import setup

with open('README.rst') as f:
    long_description = f.read()

setup(
    name='pySecurityCenter',
    version="2.0-dev",
    description='Security Center 4 API Library',
    long_description=long_description,
    author='Steven McGrath',
    author_email='steve@chigeek.com',
    url='https://github.com/SteveMcGrath/pySecurityCenter',
    packages=[
        'securitycenter',
        'securitycenter.v2',
        'securitycenter.v2.modules',
    ],
    install_requires=['requests'],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Information Technology',
        'License :: OSI Approved :: GNU Lesser General Public License v2 (LGPLv2)',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Topic :: Software Development :: Libraries :: Application Frameworks'
    ]
)
