# CSV Batch Importer Script

This script helps to fill a need for people who are trying to import a mass of asset lists into SecurityCenter 5.x.  As SC5 doesn't have a CSV import, I figured it was time to build one.

## Install (Source)

1. Installed pySecurityCenter 2.1 or greater (for SC5 Support)
2. Download Script
3. Run!

## Install (Windows)

1. Download the pre-compiled EXE
2. Run!

## Usage

The script will ask the user for all fo the relevent information before connecting to SecurityCenter.  Just make sure that you have a CSV file with the following headers (below) and in lowercase.

* addresses
* name
* description
* tags

Addresses and Name are required fields, however description and tags can be blank.  The columns do not not need to be in any particular order as the headers are informing the script where to go.  Included in this folder is a test CSV file you can use as a basis if you wish.

## Example Output

````
devbox smcgrath$ python asset_list_batch.py
CSV Batch File Path : test.csv
SecurityCenter Server : securitycenter
SecurityCenter Username : steve
SecurityCenter Password :
** Imported Test Asset 4 using 127.0.0.1
** Imported Test Asset 5 using 127.0.0.1
** Imported Test Asset 6 using 127.0.0.1
````