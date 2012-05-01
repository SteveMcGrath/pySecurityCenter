import re

fields = {
    'ip': {'name': 'IP Address'},
    'netbiosName': {'name': 'NetBIOS Name'},
    'dnsName': {'name': 'DNS Name'},
    'macAddress': {'name': 'Hardware Address'},
    'pluginID': {'name': 'Plugin ID'},
    'pluginName': {'name': 'Plugin Name'},
    'severity': {'name': 'Severity'},
    'port': {'name': 'Port'},
    'pluginText': {'name': 'Plugin Text'},
    'firstSeen': {'name': 'Days Since Discovered'},
    'lastSeen': {'name': 'Days Since Seen'},
    'firstSeenDate': {'name': 'Date Discovered'},
    'lastSeenDate': {'name': 'Date Last Seen'},
    
    # Builtin Additional Fields
    'pluginSynopsis': {
        'name': 'Synopsis', 
        'rex': re.compile(r'Synopsis :\\n\\n(.*?)\\n\\n'),
    },
    'pluginDescription': {
        'name': 'Description',
        'rex': re.compile(r'Description :\\n\\n(.*?)\\n\\n'),
    },
    'pluginSeeAlso': {
        'name': 'See Also',
        'rex': re.compile(r'See also :\\n\\n(.*?)\\n\\n'),
    },
    'pluginSolution': {
        'name': 'Solution',
        'rex': re.compile(r'Solution :\\n\\n(.*?)\\n\\n'),
    },
    'pluginRiskFactor': {
        'name': 'Risk Factor',
        'rex': re.compile(r'Risk factor :\\n\\n(.*?)\\n\\n'),
    },
    'pluginCVE': {
        'name': 'CVE',
        'rex': re.compile(r'CVE : (.*?)\\n'),
    },
    'pluginBID': {
        'name': 'BID',
        'rex': re.compile(r'BID : (.*?)\\n'),
    },
    'pluginOtherRefs': {
        'name': 'Other References',
        'rex': re.compile(r'Other references : (.*?)\\n'),
    },
    'pluginCVSS': {
        'name': 'CVSS Score',
        'rex': re.compile(r'CVSS Base Score : (.*?)\\n'),
    },
    
    # Custom Fields go here.
}