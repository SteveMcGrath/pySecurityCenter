import securitycenter
from getpass import getpass
import markdown
import re

html_head = '''
<!DOCTYPE html>  
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta http-equiv="X-UA-Compatible" content="IE=edge,chrome=1">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <style>
body{-webkit-font-smoothing:antialiased;font:normal .8764em/1.5em Arial,Verdana,sans-serif;margin:0}
html>body{font-size:13px}
li{font-size:110%}
li li{font-size:100%}
li p{font-size:100%;margin:.5em 0}
h1{color:#000;font-size:2.2857em;line-height:.6563em;margin:.6563em 0}
h2{color:#111;font-size:1.7143em;line-height:.875em;margin:.875em 0}
h3{color:#111;font-size:1.5em;line-height:1em;margin:1em 0}
h4{color:#111;font-size:1.2857em;line-height:1.1667em;margin:1.1667em 0}
h5{color:#111;font-size:1.15em;line-height:1.3em;margin:1.3em 0}
h6{font-size:1em;line-height:1.5em;margin:1.5em 0}
body,p,td,div{color:#111;font-family:"Helvetica Neue",Helvetica,Arial,Verdana,sans-serif;word-wrap:break-word}
h1,h2,h3,h4,h5,h6{line-height:1.5em}
a{-webkit-transition:color .2s ease-in-out;color:#425363;text-decoration:none}
a:hover{color:#3593d9}
.footnote{color:#0d6ea1;font-size:.8em;vertical-align:super}
#wrapper img{max-width:100%;height:auto}dd{margin-bottom:1em}
li>p:first-child{margin:0}
ul ul,ul ol{margin-bottom:.4em}
caption,col,colgroup,table,tbody,td,tfoot,th,thead,tr{border-spacing:0}
table{border:1px solid rgba(0,0,0,0.25);border-collapse:collapse;display:table;empty-cells:hide;margin:-1px 0 23px;padding:0;table-layout:fixed}
caption{display:table-caption;font-weight:700}
col{display:table-column}
colgroup{display:table-column-group}
tbody{display:table-row-group}
tfoot{display:table-footer-group}
thead{display:table-header-group}
td,th{display:table-cell}
tr{display:table-row}
table th,table td{font-size:1.1em;line-height:23px;padding:0 1em}
table thead{background:rgba(0,0,0,0.15);border:1px solid rgba(0,0,0,0.15);border-bottom:1px solid rgba(0,0,0,0.2)}
table tbody{background:rgba(0,0,0,0.05)}
table tfoot{background:rgba(0,0,0,0.15);border:1px solid rgba(0,0,0,0.15);border-top:1px solid rgba(0,0,0,0.2)}
figure{display:inline-block;margin-bottom:1.2em;position:relative;margin:1em 0}
figcaption{font-style:italic;text-align:center;background:rgba(0,0,0,.9);color:rgba(255,255,255,1);position:absolute;left:0;bottom:-24px;width:98%;padding:1%;-webkit-transition:all .2s ease-in-out}
.poetry pre{display:block;font-family:Georgia,Garamond,serif!important;font-size:110%!important;font-style:italic;line-height:1.6em;margin-left:1em}
.poetry pre code{font-family:Georgia,Garamond,serif!important}
blockquote p{font-size:110%;font-style:italic;line-height:1.6em}
sup,sub,a.footnote{font-size:1.4ex;height:0;line-height:1;position:relative;vertical-align:super}
sub{vertical-align:sub;top:-1px}
p,h5{font-size:1.1429em;line-height:1.3125em;margin:1.3125em 0}
dt,th{font-weight:700}
table tr:nth-child(odd),table th:nth-child(odd),table td:nth-child(odd){background:rgba(255,255,255,0.06)}
table tr:nth-child(even),table td:nth-child(even){background:rgba(0,0,0,0.06)}
@media print{body{overflow:auto}img,pre,blockquote,table,figure,p{page-break-inside:avoid}
#wrapper{background:#fff;color:#303030;font-size:85%;padding:10px;position:relative;text-indent:0}}
@media screen{.inverted #wrapper,.inverted{background:rgba(37,42,42,1)}
.inverted hr{border-color:rgba(51,63,64,1)!important}
.inverted p,.inverted td,.inverted li,.inverted h1,.inverted h2,.inverted h3,.inverted h4,.inverted h5,.inverted h6,.inverted pre,.inverted code,.inverted th,.inverted .math,.inverted caption,.inverted dd,.inverted dt{color:#eee!important}
.inverted table tr:nth-child(odd),.inverted table th:nth-child(odd),.inverted table td:nth-child(odd){background:0}
.inverted a{color:rgba(172,209,213,1)}
#wrapper{padding:20px}
::selection{background:rgba(157,193,200,.5)}
h1::selection{background-color:rgba(45,156,208,.3)}
h2::selection{background-color:rgba(90,182,224,.3)}
h3::selection,h4::selection,h5::selection,h6::selection,li::selection,ol::selection{background-color:rgba(133,201,232,.3)}
code::selection{background-color:rgba(0,0,0,.7);color:#eee}
code span::selection{background-color:rgba(0,0,0,.7)!important;color:#eee!important}
a::selection{background-color:rgba(255,230,102,.2)}
.inverted a::selection{background-color:rgba(255,230,102,.6)}
td::selection,th::selection,caption::selection{background-color:rgba(180,237,95,.5)}}
pre code {
  display: block; padding: 0.5em;
  color: #000;
  background: #f8f8ff
}

pre .comment,
pre .template_comment,
pre .diff .header,
pre .javadoc {
  color: #998;
  font-style: italic
}

pre .keyword,
pre .css .rule .keyword,
pre .winutils,
pre .javascript .title,
pre .lisp .title,
pre .subst {
  color: #000;
  font-weight: bold
}

pre .ruby .keyword {
  font-weight: normal
}

pre .number,
pre .hexcolor {
  color: #40a070
}

pre .string,
pre .tag .value,
pre .phpdoc,
pre .tex .formula {
  color: #d14
}

pre .title,
pre .id {
  color: #900;
  font-weight: bold
}

pre .javascript .title,
pre .lisp .title,
pre .subst {
  font-weight: normal
}

pre .class .title,
pre .haskell .label,
pre .tex .command {
  color: #458;
  font-weight: bold
}

pre .class .params {
    color: #000;
}

pre .tag,
pre .tag .title,
pre .rules .property,
pre .django .tag .keyword {
  color: #000080;
  font-weight: normal
}

pre .attribute,
pre .variable,
pre .instancevar,
pre .lisp .body {
  color: #008080
}

pre .regexp {
  color: #009926
}

pre .class {
  color: #458;
  font-weight: bold
}

pre .symbol,
pre .ruby .symbol .string,
pre .ruby .symbol .keyword,
pre .ruby .symbol .keymethods,
pre .lisp .keyword,
pre .tex .special,
pre .input_number {
  color: #0086b3
}

pre .ruby .identifier .keyword,
pre .ruby .identifier .keymethods {
  color: #0086b3;
}

pre .ruby .constant {
  color: #008080;
}

pre .builtin,
pre .built_in,
pre .lisp .title {
  color: #0086b3
}

pre .preprocessor,
pre .pi,
pre .doctype,
pre .shebang,
pre .cdata {
  color: #999;
  font-weight: bold
}

pre .deletion {
  background: #fdd
}

pre .addition {
  background: #dfd
}

pre .diff .change {
  background: #0086b3
}

pre .chunk {
  color: #aaa
}

pre .tex .formula {
  opacity: 0.5;
}

#header {
    background: #425363;
    height: 73px;
    width: 100%;
}

#logo {
    height: 73px;
}
</style>

</head>
<body class="normal">
  <div id="header">
    <img id="logo" src="data:image/png;base64,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" alt="logo-teal.png" />
  </div>
  <div id="wrapper">
'''


def main():
    '''Main Program Loop'''

    # First we need to get the login information.
    print 'Security Center Remediation Report Generator\n----------------------------------------------'
    sc_address = raw_input('Address : ')
    sc_user = raw_input('Username : ')
    sc_pass = getpass('Password : ')
    try:
        sc = securitycenter.SecurityCenter4(sc_address)
        sc.login(sc_user, sc_pass)
    except:
        print 'Invalid Host or Account Information.'
        exit()

    # Next Determine how we want to limit the data.
    data = sc.assets()
    print 'Repositories\n------------'
    for repo in data['repositories']:
        print repo['id'], repo['name']
    repos = raw_input('Repository ID : ').strip()

    print '\nAssets\n------'
    for asset in data['assets']:
        print asset['id'], asset['name']
    asset = raw_input('Asset List ID : ').strip()

    try:
        reponame = [r['name'] for r in data['repositories'] if r['id'] == repos][0]
        if asset != '':
          assetname = [a['name'] for a in data['assets'] if a['id'] == asset][0]
    except:
        print 'Either the Repository ID or the Asset ID are invalid.'
        exit()

    report_name = raw_input('Report Output Filename : ')

    # Now to get the data
    filterset = {
      'pluginID': '66334', 
      'repositoryIDs': repos,
    }
    if asset != '':
      filterset['assetID'] = asset
    print '\n* Querying Security Center...'
    try:
        details = sc.query('vulndetails', **filterset)
    except securitycenter.APIError, msg:
        print str(msg).replace('\\n','\n')
        exit()

    report = open('%s.md' % report_name, 'w')
    skipper = []
    # Chapter 1: Discovered Hosts
    print '* Building Chaper 1'
    report.write('# Discovered Systems\n\n')
    report.write(' * __Repository :__ %s\n' % reponame)
    if asset != '':
      report.write(' * __Asset List :__ %s\n' % assetname)
    report.write('\n')
    report.write('|IP|NetBIOS|Operating System|Risk|Patches|Low|Medium|High|Critical|\n')
    report.write('|:-|:------|:---------------|:---|:------|:--|:-----|:---|:-------|\n')
    for item in details:
        info = sc.ip_info(item['ip'], [repos])['records'][0]
        rems = sc.query('sumremediation', repositoryIDs=repos, ip=item['ip'])
        if len(rems) > 0:
          print 'Building Summary for %s...' % item['ip']
          report.write('|[%s](#%s)|%s|%s|%s|%s|%s|%s|%s|%s|\n' % (item['ip'], item['ip'],
                                                  info['netbiosName'],
                                                  info['os'].replace('<br/>', ' '),
                                                  info['score'],
                                                  len(rems),
                                                  info['severityLow'],
                                                  info['severityMedium'], 
                                                  info['severityHigh'], 
                                                  info['severityCritical']))
        else:
          skipper.append(item['ip'])

    # Chapter 2: Detail
    print '* Building Chapter 2'
    pout = re.compile('<plugin_output>(.*)</plugin_output>')
    ms = re.compile(r'- {0,1}(KB[^\<\:\n]*)')
    fix1 = re.compile(r'- (.* \(\d{5,6}\):)((?:\n(?! -).*){1,})')
    fix2 = re.compile(r'\[ (.*) \]\n\n\+ Action to take: (.*)\n\n\+ Impact: (.*)')
    kbids = re.compile(r'KB(\d{6,8})')
    msids = re.compile(r'(MS\d{2}\-\d{2,3})')
    msvulns = re.compile(r'\((\d{1,3}) vulnerabilit')
    report.write('\n# Remediation Plan\n')
    for item in details:
        if item['ip'] in skipper:
          continue
        # We need to parse out all of the data using regex
        item['pOut'] = pout.findall(item['pluginText'])[0].replace('<br/>','\n')
        item['MSBulletins'] = ms.findall(item['pOut'])
        item['patch'] = fix1.findall(item['pOut'])
        [item['patch'].append(a) for a in fix2.findall(item['pOut'])]

        # And now to write the item in the chapter...
        report.write('\n\n## <a id="%s"></a>Remediation Plan for %s\n\n' % (item['ip'], item['ip']))
        if len(item['MSBulletins']) > 0:
            report.write('\n__To patch the remote system, you need to install the following Microsoft patches:__\n\n')
            for kba in item['MSBulletins']:
                entry = '  * '
                kbid = kbids.findall(kba)
                msid = msids.findall(kba)
                vnum = msvulns.findall(kba)
                if len(kbid) > 0:
                    entry += '[KB%s](http://support.microsoft.com/kb/%s) ' % (kbid[0], kbid[0])
                if len(msid) > 0:
                    entry += '([%s](http://technet.microsoft.com/en-us/security/bulletin/%s))' % (msid[0], msid[0])
                if len(vnum) > 0:
                    vnum = int(vnum[0])
                    if vnum == 1:
                        entry += ' (1 vulnerability)'
                    else:
                        entry += ' (%s vulnerabilities)' % vnum
                if entry == '  * ':
                    entry += kba
                report.write('%s\n' % entry)
        if len(item['patch']) > 0:
            report.write('\n__You need to take the following %d actions:__\n\n' % len(item['patch']))
            for patch in item['patch']:
                if len(patch) == 2:
                    report.write('  * %s\n' % patch[0])
                    report.write('    * %s\n' % patch[1].replace('\n', ' '))
                if len(patch) == 3:
                    report.write('  * %s\n' % patch[0])
                    report.write('    * __Action to take :__ %s\n' % patch[1])
                    report.write('    * __Impact :__ %s\n' % patch[2])

    report.close()

    # Now to Generate the PDF...
    print '* Saving HTML File...'
    with file('%s.html' % report_name, 'w') as html:
        html.write(html_head)
        html.write(markdown.markdown(file('%s.md' % report_name).read(), ['tables']))
        html.write('</div></body></html>')


if __name__ == '__main__':
    main()
