from setuptools import setup
import os

long_description = ''
try:
    from pypandoc import convert
    if os.path.exists('README.md'):
        long_description = convert('README.md', 'rst')
except ImportError:
    print("warning: pypandoc module not found, could not convert README.md to RST")


setup(
    name="pySecurityCenter",
    version='2.1.6',
    description="Security Center API Library",
    long_description='Python Interface into Tenable\'s SecurityCenter',
    author=', '.join([
        'Steven McGrath <steve@chigeek.com>', 
        'David Lord <davidism@gmail.com>',
    ]),
    author_email="steve@chigeek.com",
    url="https://github.com/SteveMcGrath/pySecurityCenter",
    packages=[
        "securitycenter",
        "securitycenter.orm",
        "securitycenter.orm.modules",
    ],
    install_requires=["requests"],
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Information Technology",
        "License :: OSI Approved :: BSD License",
        "Natural Language :: English",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 2.4",
        "Programming Language :: Python :: 2.6",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Topic :: Software Development :: Libraries :: Application Frameworks"
    ]
)
