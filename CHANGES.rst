Changelog
=========

Version 2.0-dev
---------------

*In development*

This is a large rewrite to make the API more modular and easy to extend.
Support is dropped for 2.4 and 2.5.  Started by davidism.

- Actions are namespaced by their module, much like the acutal API.  For
  example, to call `plugin::init`, use `sc.plugin.init()`.
- Switch to the Requests library for API calls.  This drops support for < 2.6.
    - Requests handles cookies and SSL
- Use the 4.6 API.
- Add many more (undocumented) modules.
    - The scan module allows starting scans outside the canonical frontend

Version 1.0
-----------

- Changed Rev to 1.x as the code has been sufficiently stable.
- Added proper error handling for login [davidism]
- Handling of Datetime objects now works as expected [davidism]

Version 0.3.9
-------------

- Removed un-needed poster requirement [davidism]
- Improved scan_list time handling [davidism]
- Added support for Two-way SSL Certificates [davidism]

Version 0.3.8
-------------

- Added proper support for individual scan results in the query function. [davidism]
- Added this README to the package (for pypi)

Version 0.3.7
-------------

- Added pagination support to plugins function. [davidism]

Version 0.3.6
-------------

- Added Python 2.4 Support

Version 0.3.5
-------------

- Added "patched" source to conform to SC 4.6

Version 0.3.4
-------------

- Added debug logging support.

Version 0.3.3.1
---------------

- Updated to support Python 2.6, 2.7, and 3.x
- Completed documentation of module.

Version 0.3.2
-------------

- Added Dashboard and Report Importing

Version 0.3.1
-------------

- Added Scan Download Capability
- Fixed roles return
- Adjusted login process
- Added Credential functions
- Code Cleanup
- Fleshed out all functions to match SC 4.2 API docs.
