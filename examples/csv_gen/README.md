## CSV Generator


###Description

csv_gen is a python script designed to pull the vulnerability data from
the asset lists that are defined with the configuration file, parse out
any extra fields needed from the plugin text field, and then build a CSV
file with all the data and email that out to the corresponding people.
The script is designed to be run centrally with multiple reports being
generated and delivered to different people or groups of people as needed,
and to help facilitate in breaking out needed data from the plugin text
field.
    
This script is also flexible enough to allow for additional fields to be
build from the plugin text field if needed.  If this is needed, then you
would simply need to extent the plugin_fields dictionary at the beginning
of the csv_gen script.

__Requirements:__

* __Python 2.6 or 2.7__<br />
  Python 3.x or <2.6 will not work.  This script depends on the json
  libraries that were included in 2.6.  The script was build and 
  tested using Python 2.7.1+
* __Open SMTP Server__<br />
  This SMTP server can be running on the local box and configured to
  only talk to localhost if needed.  All testing was done using this
  configuration using Postfix.
* __pySecurityCenter__<br />
  pySecurityCenter is the python Security Center module needed in order
  for the CSV generator to interact with the SC4 API.

__Installation:__

1.  Extract the contents of the zip file to the location that you want to
    run the script from.
    
2.  Make sure that the user that will be running the script has read,
    write, and execute permissions on the files directory.  All of the
    data generated is staged in this location and without this, the script
    will fail.
    
3.  Copy the config.ini.sample to config.ini and adjust to suit your
    needs.  For testing it is recommended to turn on debugging and run the 
    script manually until the desired output has been generated.  When 
    ready to run in a production-setting, make sure to turn off the 
    debugging to prevent the output from spamming root's mailbox.
    
4.  Build a cronjob to run the script when needed.  Keep in mind that this
    script can create a heavy load on the Security Center installation and
    plan accordingly.  An exmaple crontab entry is like so:
        
    `00 4 * * * csvuser /usr/bin/python /opt/csv_gen/csv_gen.py`
   
5.  Your Done!

__Version History:__

1.0.0:

  - Complete Rewrite
  
  - Restructured to use a modular nature.  Easier to debug and adjust this
    way.
  
  - Reworked how data is fundamentally queries from the api.  This is now
    done using a filterset instead of relying only on a asset list.

  - Added the ability for individual csv file definitions to contain their
    own email subjects and bodys.

0.3.2:

  - Restricted dataset to non-mitigated, non-accepted risks.

0.3.1:

  - Added Date Fields.
    
0.3:

  - Support for customizable reports.  Fields and the order are now
    specified on a per-asset configuration basis.
        
  - Restructured code to write data inline with API calls.  This
    resolves an issue with very large CSV files consuming over 1GB of
    RAM.  The current script in default configuration has not consumed
    more than ~160MB on a 135,000+ result query.
    
0.2:

  - Windows Support.  All of the code now uses os.path.join to ensure
    OS independence.
        
  - Various bug fixes.
    
0.1:

  - Initial Version.