import httplib
import json
from urllib import urlencode

class SCBase(object):
  _token  = None
  _host   = None
  _conn   = httplib.HTTPSConnection
  _cookie = None
  _raw    = True
  
  def __init__(self, username, password, host, ssl=True, raw=True):
    '''
    SC4 API Initialization method.
    
    Required:
      username  = String
      password  = String
      host      = String
    
    Optional:
      ssl       = Boolean (Default True)
    '''
    self._host = host
    self._raw = raw
    if ssl:
      self._conn = httplib.HTTPConnection
    else:
      self._conn = httplib.HTTPSConnection
    self._login(username, password)
  
  def _login(self, username, password):
    data = self._request('auth','login', 
                         data={'username': username, 'password': password})
    self._token = data['response']['token']
    self.user   = data
  
  def _request(self, module, action, url='/sc4/request.php', 
               data={}, headers={}, json_encode=True):
    '''
    INTERNAL METHOD: Root method for talking to security center.
    '''
    data = {
      'request_id': 1,
      'module': module,
      'action': action,
      'input': json.dumps(data)
    }
    if self.token is not None:
      data['token'] = self._token
    if self.cookie is not None:
      headers['Cookie'] = self._cookie
    headers['Content-Type'] = 'application/x-www-form-urlencoded'
    headers['Content-Length'] = len(payload)
    http = self._conn(self._host)
    http.request('POST', url, body=payload, headers=headers)
    resp = http.getresponse()
    if resp.getheader('set-cookie') is not None:
      self._cookie = resp.getheader('set-cookie')
    if json_encode:
      return json.loads(resp.read())
    else:
      return resp.read()
  
  def logout(self):
    self._request('auth','logout', data={'token': self._token})
    self._token = None
    self.user = None

  def send(self, module, action, data={}):
    return self._request(module, action, data=data)
  
  def alerts(self):
    return self.send('alert', 'init')
  
  def assets(self):
    return self.send('asset', 'init')
  
  def asset_update(self, **data):
    return self.send('asset', 'edit',data=data)
  
  def asset_get_ips(self, asset_id):
    return self.send('asset', 'getIPs', data={'id'=asset_id})
  
  def credentials(self):
    return self.send('credential', 'init')
  
  def credential_update(self, **data):
    return self.send('credential', 'edit',data=data)
  
  def events(self, **data):
    return self.send('events', 'query', data=data)
  
  def plugins(self):
    return self.send('plugin', 'init')
  
  def plugin_details(self, plugin_id):
    return self.send('plugin', 'getDetails', data={'pluginID': plugin_id})
  
  def plugin_search(self, **data):
    return self.send('plugin', 'getPage', data=data)
  
  def repositories(self):
    return self.send('repository', 'init')
  
  def roles(self):
    return self.send('role', 'init')
  
  def system(self):
    return self.send('system', 'init')
  
  def tickets(self):
    return self.send('ticket', 'init')
  
  def users(self):
    return self.send('users', 'init')
  
  def vulns(self):
    return self.send('vuln', 'init')
  
  def vuln_get_ip(self, ip, repositories):
    repos = []
    for item in repositories:
      repos.append({'id': item})
    return self.send('vuln', 'getIP', data={'ip': ip, 'repositories': repos})
  
  def vuln_search(self, **data):
    return self.send('vuln', 'query', data=data)
  
  def zones(self):
    return self.send('zone', 'init')