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
    version='3.0.0',
    description="Security Center API Library",
    long_description='Python Interface into Tenable\'s SecurityCenter',
    author='Steven McGrath <steve@chigeek.com>',
    author_email="steve@chigeek.com",
    url="https://github.com/SteveMcGrath/pySecurityCenter",
    packages=["securitycenter",],
    install_requires=["requests",],
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Information Technology",
        "License :: OSI Approved :: BSD License",
        "Natural Language :: English",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 2.6",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Topic :: Software Development :: Libraries :: Application Frameworks"
    ]
)
