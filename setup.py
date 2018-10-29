from setuptools import setup
import os

try:
    long_description = open(
        os.path.join(
            os.path.abspath(os.path.dirname(__file__)),
            'README.rst')).read()
except:
    long_description = 'Please refer to https://pytenable.readthedocs.io'
    print('! could not read README.rst file.')

setup(
    name="pySecurityCenter",
    version='3.1.2',
    long_description=long_description,
    description="Security Center API Library",
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
