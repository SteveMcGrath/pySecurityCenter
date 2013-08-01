from setuptools import setup

setup(
    name="pySecurityCenter",
    version="2.0-dev",
    description="Security Center 4 API",
    author="Steven McGrath",
    author_email="smcgrath@tenable.com",
    url="https://github.com/SteveMcGrath/pySecurityCenter",
    packages=["securitycenter"],
    install_requires=["requests"],
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Intended Audience :: Information Technology",
        "License :: OSI Approved :: GNU Lesser General Public License v2 (LGPLv2)",
        "Natural Language :: English",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 2.6",
        "Programming Language :: Python :: 2.7",
        "Topic :: Software Development :: Libraries :: Application Frameworks"
    ]
)
