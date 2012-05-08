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
        'rex': [
            re.compile(r'Synopsis :\\n\\n(.*?)\\n\\n'),
            re.compile(r'<synopsis>(.*?)</synopsis>'),
        ],

    },
    'pluginDescription': {
        'name': 'Description',
        'rex': [
            re.compile(r'Description :\\n\\n(.*?)\\n\\n'),
            re.compile(r'<description>(.*?)</description>'),
        ],
    },
    'pluginSeeAlso': {
        'name': 'See Also',
        'rex': [
            re.compile(r'See also :\\n\\n(.*?)\\n\\n'),
            re.compile(r'<see_also>(.*?)</see_also>'),
        ],
    },
    'pluginSolution': {
        'name': 'Solution',
        'rex': [
            re.compile(r'Solution :\\n\\n(.*?)\\n\\n'),
            re.compile(r'<solution>(.*?)</solution>'),
        ],
    },
    'pluginRiskFactor': {
        'name': 'Risk Factor',
        'rex': [
            re.compile(r'Risk factor :\\n\\n(.*?)\\n\\n'),
            re.compile(r'<risk_factor>(.*?)</risk_factor>'),
        ],
    },
    'pluginCVE': {
        'name': 'CVE',
        'rex': [
            re.compile(r'CVE : (.*?)\\n'),
            re.compile(r'<cve>(.*?)</cve>'),
        ],
    },
    'pluginBID': {
        'name': 'BID',
        'rex': [
            re.compile(r'BID : (.*?)\\n'),
            re.compile(r'<bid>(.*?)</bid>'),
        ],
    },
    'pluginOtherRefs': {
        'name': 'Other References',
        'rex': [
            re.compile(r'Other references : (.*?)\\n'),
            re.compile(r'<xref>(.*?)</xref>'),
        ],
    },
    'pluginCVSS': {
        'name': 'CVSS Score',
        'rex': [
            re.compile(r'CVSS Base Score : (.*?)\\n'),
            re.compile(r'<cvss_base_score>(.*?)</cvss_base_score>'),
        ],
    },
    'exploitFramework': {
        'name': 'Exploit Framework',
        'rex': [
            re.compile(r'<exploit_framework_(\w*?)>'),
        ],
    },
    'pluginOutput': {
        'name': 'Plugin Output',
        'rex': [
            re.compile(r'<plugin_output>(.*?)</plugin_output>')
        ],
    }
    
    # Custom Fields go here.
}