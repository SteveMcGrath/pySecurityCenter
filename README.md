# Python Security Center Module

This module is designed to attempt to make interfacing with Security Center's
API easier to use and more manageable.  A lot of effort has been put into making
queries into the API as painless and manageable as possible.

[Source Code Repository](https://github.com/SteveMcGrath/pySecurityCenter)

For Tenable.io API work, you may want to look at the official python SDK:

[Tenable.io Python SDK](https://github.com/tenable/Tenable.io-SDK-for-Python)

# Changelog

__v3.0__

* Removed the ORM SecurityCenter 4 code (still referencable in older versions)
* Migrated the SecurityCenter 4 module to use the base module, bringing it in line with the rest of the modules.
* New Nessus class.
* New PVS class.
* Code should now work with Python 2.6+ (incl 3.x) without the need for 2to3 anymore.
* Dropped Python 2.4 support

__v2.1__

* Added support for SecurityCenter 5.  This is called via the base API and
  is the SecurityCenter5 class.

__v2.0a5__

* Reworked the setup.py file to handle converting the readme to restructured
  text for use with pypi.  further if the readme file doesn't exist, just throw
  a warning and move on.

__v2.0a2__

* Pulled in the 75~ commits from David with the ORM code.
* Reworked the code to use the orm/base standpoint instead of v1/v2

__v2.0a1__

* Initial rev with David's merged ORM code.
* All ORM code is to be considered Alpha for now.
* Added stubs in the API base for SecurityCenter 5 when released.

__v1.1__

* Changed the module structure to support the ORM model from David
* Fixed the Asset update to support SC4.8's switch to tagging and groups

__v1.0__

* Changed Rev to 1.x as the code has been sufficiently stable.
* Added proper error handling for login [davidism]
* Handling of Datetime objects now works as expected [davidism]

__v0.3.9__

* Removed un-needed poster requirement [davidism]
* Improved scan_list time handling [davidism]
* Added support for Two-way SSL Certificates [davidism]

__v0.3.8__

* Added proper support for individual scan results in the query function. [davidism]
* Added this README to the package (for pypi)

__v0.3.7__

* Added pagination support to plugins function. [davidism]

__v0.3.6__

* Added Python 2.4 Support

__v0.3.5__

* Added "patched" source to conform to SC 4.6

__v0.3.4__

* Added debug logging support.

__v0.3.3.1__

* Updated to support Python 2.6, 2.7, and 3.x
* Completed documentation of module.

__v0.3.2__

* Added Dashboard and Report Importing

__v0.3.1__

* Added Scan Download Capability
* Fixed roles return
* Adjusted login process
* Added Credential functions
* Code Cleanup
* Fleshed out all functions to match SC 4.2 API docs.


# How to Install

To install pySecurityCenter, you can use either pip or easy_install to install
from the cheeseshop:

`pip install pysecuritycenter`

`easy_install pysecuritycenter`

If you would rather install manually, feel free to download the latest version
directly from the [cheeseshop][]:

[cheeseshop]: http://pypi.python.org/pypi/pySecurityCenter

# Usage

* For SecurityCenter4, please see the [SC4 pySecurityCenter Documentation][sc4base].
* For SecurityCenter5, please see the [SC5 pySecurityCenter Documentation][sc5base].

[sc4base]: https://github.com/SteveMcGrath/pySecurityCenter/blob/master/SecurityCenter4_Base_API.md
[sc5base]: https://github.com/SteveMcGrath/pySecurityCenter/blob/master/SecurityCenter5_REST_API.md
