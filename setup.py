from setuptools import setup
import securitycenter

with open("README.md") as f:
    long_description = f.read()

setup(
    name="pySecurityCenter",
    version=securitycenter.__version__,
    description="Security Center API Library",
    long_description=long_description,
    author=", ".join(securitycenter.__authors__),
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
        "License :: OSI Approved :: GNU Lesser General Public License v2 (LGPLv2)",
        "Natural Language :: English",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 2.4",
        "Programming Language :: Python :: 2.6",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Topic :: Software Development :: Libraries :: Application Frameworks"
    ]
)
