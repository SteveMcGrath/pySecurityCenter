#!/usr/bin/env python
from securitycenter import SecurityCenter5
from BeautifulSoup import BeautifulSoup
from csv import DictWriter


def builder(**kwargs):
	report = kwargs['report']	# The CSV Report
	sc = kwargs['sc']			# SecurityCenter
	vulns = kwargs['resp'].json()['response']['results']	# The vuln data
	os = None					# The OS of the current host
	responsibility = None		# The user responsible for the current host
	device = None				# The current device IP
	for vuln in vulns:
		if device != vuln['ip']:
			# If the device does not match the current host that we are on, then
			# We need to re-query the API and get the OS and the User(s) that
			# are responsible.
			results = sc.analysis(('ip', '=', vuln['ip']), tool='listos')
			if len(results) > 0:
				os = '/'.join([r['name'] for r in results])
			# We need to perform the User Responsibility stuff here as well...
			device = vuln['ip']

		# New we will build a BeautifulSoup object to parser out the needed info
		# from the PluginText returned.
		content = BeautifulSoup(vuln['pluginText'])
		expected = content.find('cm:compliance-policy-value')
		actual = content.find('cm:compliance-actual-value')
		print content
		report.writerow({
			'Status': content.find('cm:compliance-result').text,
			'Hostname': vuln['dnsName'],
			'IP Address': vuln['ip'],
			'Info': content.find('cm:compliance-info').text,
			'Expected Value': expected.text if expected else '',
			'Actual Value': actual.text if actual else '',
			'Operating System': os,
			'User Responsibility': responsibility
		})
	return []	# The SC5 analysis function expects a list to be returned.


if __name__ == '__main__':
	HOSTNAME = 'HOSTNAME'
	USERNAME = 'USERNAME'
	PASSWORD = 'PASSWORD'
	QUERY = (
		('pluginType', '=', 'compliance'),
	)

	sc = SecurityCenter5(HOSTNAME)
	sc.login(USERNAME,PASSWORD)

	reportfile = open('report.csv', 'w')
	report = DictWriter(reportfile,
		[
			'Status', 
			'Hostname', 
			'IP Address', 
			'Info',
			'Expected Value',
			'Actual Value', 
			'Operating System', 
			'User Responsibility'
		],
	)
	
	report.writeheader()
	sc.analysis(*QUERY, tool='vulndetails', page_obj=builder, page_kwargs={'report': report, 'sc': sc})
	reportfile.close()