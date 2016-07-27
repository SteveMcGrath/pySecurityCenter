# Basic Usage

The SecurityCenter 5 RESTful API is a significant departure from the JSON/RPC API that SecurityCenter 4 had used.  As a result of that, a different methodology was approached to building the API linkage into python.  The SC5 module leverages the request module to handle communication between your python code and the API.  Further because of this, a lot of the functions that used to be needed in order to make the module useful are no longer needed.  Connecting to SecurityCenter using the SC5 API is as simple as the following:

````
>>> from securitycenter import SecurityCenter5
>>> sc = SecurityCenter5('HOSTNAME')
>>> sc.login('USERNAME','PASSWORD')
````

Instead of functionalizing every API call thats available, the methodology instead is to provide a base layer into the API, and only functionalize things that are seen to be difficult and/or cumbersome to handle gracefully.  As a result of this, the calls that will be primarily used here are the following:

* sc.get()
* sc.post()
* sc.put()
* sc.patch()
* sc.delete()
* sc.head()

The SecurityCenter5 object will prepend all of the relevant connection information and base API slug.  So for example, to get the current status of the SecurityCenter system, you will need to perform the following:

````
response = sc.get('status')
````

There has been a convenience function added for querying the system, as the analysis API call has a lot of capability, and as such, leverages a fairly complex call.  You are of course welcome to use a sc.post call to perform this operation yourself, but `sc.analysis()` is there to make your life a little easier.

Firstly, the analysis function is coded a bit differently than the query is in the SC4 API.  This is an attempt to both make the function more useful, as well as to conform to the new API calls behind the scene.  For example, to get the top 100 most vulnerable hosts, you would perform the following:

````
hosts = sc.analysis(tool='sumip', page=0, page_size=100, sortDir='desc', sortField='score')
````

Now if we only wanted the hosts that were part of the 10.10.0.0/16 network range, we would make the following changes:

````
homenet_hosts = sc.analysis(('ip', '=', '10.10.0.0/16'), tool='sumip', page=0, page_size=100, sortDir='desc',sortField='score')
````

Filters always exist at the front of the call, and multiple can exist in the same query.  For example, if I wanted the vulnerability details of plugin ID 20811 for the hosts in 10.10.0.0/16, I would do the following:

````
details = sc.analysis(('ip', '=', '10.10.0.0/16'), ('pluginID', '=', '20811'), tool='vulndetails')
````

To send multiple values, use a comma delimited strings (where the API Supports it):

````
details = sc.analysis(('ip', '=', '10.10.0.0/16'), ('severity', '=', '3,4'), tool='vulndetails')
````

There is also an `sc.upload()` function that accepts a file object.  It will return with the relevant information (including things like the temporary filename you will need in the subsequent calls).

For more information as to whats possible, please see the [Tenable API documentation][apidocs].  Further, there are cases where forcibly sending a bad call (such as an analysis call without a tool) will let you know what can be done.

[apidocs]: https://support.tenable.com/support-center/cerberus-support-center/includes/widgets/sc_api/index.html

To better understand what arguments are available for get/post/put/patch/delete/head, please see the [python-requests documentation][requests].

[requests]: http://docs.python-requests.org/en/latest/


Please note that this document will be expanded upon over time.
