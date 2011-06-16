import httplib
import json
from urllib import urlencode

class SecurityCenter(object):
  token = None
  host = None
  conn = None
  cookie = None
  
  def __init__(self, username, password, host, ssl=True):
    self.host = host
    if ssl:
      self.conn = httplib.HTTPConnection
    else:
      self.conn = httplib.HTTPSConnection
    self._login(username, password)
  
  def _request(self, module, action, url='/sc4/request.php', 
               data={}, headers={}, json_encode=True):
    data = {
      'request_id': 1,
      'module': module,
      'action': action,
      'input': json.dumps(data)
    }
    if self.token is not None:
      data['token'] = self.token
    if self.cookie is not None:
      headers['Cookie'] = self.cookie
    headers['Content-Type'] = 'application/x-www-form-urlencoded'
    headers['Content-Length'] = len(payload)
    http = self.conn(self.host)
    http.request('POST', url, body=payload, headers=headers)
    resp = http.getresponse()
    if resp.getheader('set-cookie') is not None:
      self.cookie = resp.getheader('set-cookie')
    if json_encode:
      return json.loads(resp.read())
    else:
      return resp.read()
  
  def _login(self, username, password):
    data = self._request('auth','login', 
                         data={'username': username, 'password': password})
    self.token = data['response']['token']
  
  def logout(self):
    self._request('auth','logout')
    self.token = None
  
  def send(self, module, action, data={}):
    return self._request(module, action, data=data)