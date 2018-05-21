from securitycenter import SecurityCenter5 
from datetime import datetime, timedelta
from json2html import *
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import config
import smtplib 
import json

'''
Author: David Frazer - https://github.com/maravedi
Date: 3/14/2018
Description: A script to query the SecurityCenter API for newly assigned tickets based on a set timeframe. This script will send an email to the assignee of each ticket
	     matching the specified parameters. One single email will be delievered that includes the details from each ticket that matches the parameters. 
'''

def get_info(sc):
    now = datetime.now()
    # Set how far to look back. For this situation, we are looking back to the last 30 minutes.
    # We will use this to get tickets between thirty minutes ago and now.
    starttime = (now + timedelta(minutes=-30))

    # Query the SecurityCenter API's ticket resource.
    alltickets = sc.get('ticket', params={'fields': 'name,description,classification,status,notes,assignee,assignedTime,resolvedTime'}).json()['response']['usable']
    ticketsbyid = {}
    
    # Here we are filtering down the tickets since we cant' do that in the actual API query.
    # Find tickets that don't have a resolvedTime set.
    opentickets = [item for item in alltickets if item['resolvedTime'] == '-1']
    # Find tickets that have a status of assigned.
    assignedtickets = [item for item in alltickets if item['status'] == 'assigned']
    # Use our time values set above to find tickets that were assigned within the specified timeframe.
    newtickets = [item for item in assignedtickets if (starttime <= (datetime.fromtimestamp(float(item['assignedTime']))) <= now)]

    # Iterate through the tickets to generate a dictionary that uses custom keys, some value modification, and also pulls in the email address of the user set as the assignee.
    for ticket in newtickets:
        ticketid = int(ticket['id'])
        assigneeid = int(ticket['assignee']['id'])
	# Query the SecurityCenter API's user resource for the assignee's email address using the assignee's ID.
        assigneeemail = sc.get('user/%s' % assigneeid, params={'fields': 'email'}).json()['response']['email']
	# Convert the assignedTime from epoch time to a timestamp, and then convert it to a human-readable datetime string.
        assignedtime = datetime.fromtimestamp( float(ticket['assignedTime']) )
        assignedtimestring = assignedtime.strftime("%m/%d/%y %I:%M %p")

	# Add the details for this particular ticket to the dictionary.
        ticketsbyid[ticketid] = {
            'Ticket ID': ticketid,
            'Ticket Title': ticket['name'],
            'Ticket Description': ticket['description'],
            'Assignee Email': assigneeemail,
            'Assignee': ticket['assignee']['firstname'] + " " + ticket['assignee']['lastname'],
            'Assigned Time': assignedtimestring,
            'Ticket Status': (ticket['status']).capitalize(),
            'Ticket Classification': ticket['classification'],
            'Ticket Notes': ticket['notes'],
        }
    # Return the ticket dictionary.
    return ticketsbyid

def send_info(ticketdata):

    # Here we build a dictionary that contains the assignee email address as the key and each ticket ID assigned to them as the values.
    # This allows us to iterate over the tickets by email address.
    ticketsbyuser = {}
    for item in ticketdata:
	# This is a fallback in case the user set as the assignee does not have an email adddress set. In that case, this script will send the email to the email address
	# configured in the config file as scriptadmin.
	if len(ticketdata[item]['Assignee Email']) == 0:
	    try:
	        ticketsbyuser[config.scriptadmin] += [ticketdata[item]['Ticket ID']]
	    except KeyError:
		ticketsbyuser[config.scriptadmin] = [ticketdata[item]['Ticket ID']]
	# The user set as the assignee does have en email configured, so we'll set it as the key to the ticketsbyuser dictionary.
	else:
            try:
                ticketsbyuser[str(ticketdata[item]['Assignee Email'])] += [ticketdata[item]['Ticket ID']]
            except KeyError:
                ticketsbyuser[str(ticketdata[item]['Assignee Email'])] = [ticketdata[item]['Ticket ID']]

    # Iterate through each email in the dictionary to build the HTML for the email to be delivered to the assignee.
    for email in ticketsbyuser:
	# Some styling to make the email less bland. These colors match some of the colors used in the SecurityCenter web interface, as of version 5.
        html = """
        <style>
        body {
            color: #425363;
            font: 'Helvetica Neue',helvetica,arial,sans-serif;
            font-size: 13px;
        }
        td, th {
            border: 0px solid #425363;
            border-collapse: collapse;
            word-wrap: break-word;
        }
        th {
            background-color: #eeeff0;
        }
        table, tr, td, th {
            padding: 2px;
            margin: 0px;
        }
        tr:nth-child(odd) {
            background-color: #eee; 
        }
        table {
            margin-left: 5px;
        }
        </style>"""
	# Check to see if this user has just one ticket, or if they have more. We will dynamically change the email
	# subject to use the appropriate language for each.
        if len(ticketsbyuser[email]) == 1:
            html += "<h3>The following new ticket has been assigned to you in SecurityCenter:</h3>"
        else:
            html += "<h3>The following new tickets have been assigned to you in SecurityCenter:</h3>"
	# Iterate over the ticket IDs for this user and build the HTML tables for each ticket.
        for id in ticketsbyuser[email]:
	    # Note that we're just converting the dictionary to html and sorting it. Any modifications to the keys or values needs to be
	    # performed during the building of the dictionary in the get_info function.
            html += "%s" % json2html.convert(json = json.dumps(ticketdata[id], sort_keys = True))
	    # Add a link to the ticket so the recipient can go directly to the ticket from the email.
            html += '&nbsp;&nbsp;<a href="https://' + config.servername + '/#tickets/view/%d">View Ticket</a><br><br>' % id
        html += "<br><br><i>Note: This email provides only a summary of the ticket. Please view the ticket in SecurityCenter for full details."
        server = smtplib.SMTP(config.smtpserver, 25)
        emailfrom = config.emailfrom
        emailto = email
        msg = MIMEMultipart('alternative')
        msg['Subject'] = "New Ticket Assigned in SecurityCenter"
        msg['From'] = emailfrom
        msg['To'] = emailto
        mime = MIMEText(html, 'html')
        msg.attach(mime)
        server.sendmail(emailfrom, emailto, msg.as_string())
        server.quit()
if __name__ == '__main__':
    sc = SecurityCenter5(config.servername)
    sc.login(config.username, config.password)
    # Get the ticket data
    ticketlist = get_info(sc)
    # Send the ticket data
    send_info(ticketlist)
    sc.logout()
