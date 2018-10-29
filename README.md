# NOTICE: Deprecated.  All future work being done on pyTenable.

pySecurityCenter predates my employment at tenable (going back now 8+ years) and as there is finally an official module being built, this module should be ignored in favor of the official module.  The official module is being built to incorporate a lot of the lessons learned over the years with pySC.  I welcome community input, pulls, feedback, etc.  Lets make the official module so much better than pySC ever was!

https://github.com/tenable/pytenable

pyTenable version 0.2 has the same level of functionality that pySC does,
and aside from some minor changes (for the better) to the analysis endpoint, should work the same way out of the box.

# Original Readme

## Python Security Center Module

This module is designed to attempt to make interfacing with Security Center's
API easier to use and more manageable.  A lot of effort has been put into making
queries into the API as painless and manageable as possible.

[Source Code Repository](https://github.com/SteveMcGrath/pySecurityCenter)

For Tenable.io API work, you may want to look at the official python SDK:

[Tenable.io Python SDK](https://github.com/tenable/Tenable.io-SDK-for-Python)

## How to Install

To install pySecurityCenter, you can use either pip or easy_install to install
from the cheeseshop:

`pip install pysecuritycenter`

`easy_install pysecuritycenter`

If you would rather install manually, feel free to download the latest version
directly from the [cheeseshop][]:

[cheeseshop]: http://pypi.python.org/pypi/pySecurityCenter

## Usage

* For SecurityCenter4, please see the [SC4 pySecurityCenter Documentation][sc4base].
* For SecurityCenter5, please see the [SC5 pySecurityCenter Documentation][sc5base].

[sc4base]: https://github.com/SteveMcGrath/pySecurityCenter/blob/master/SecurityCenter4_Base_API.md
[sc5base]: https://github.com/SteveMcGrath/pySecurityCenter/blob/master/SecurityCenter5_REST_API.md
