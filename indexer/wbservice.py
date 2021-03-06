import requests
from requests.auth import HTTPBasicAuth
import json
import logging

logger = logging.getLogger(__name__)

headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}

class WebService(object):
  def __init__(self, base_url, user = None, password = None):
    self.base_url = base_url
    if user:
      logger.info("Using credentials (%s) to connect to %s" % (user, base_url))
    self.user = user
    self.password = password

  def _call_endpoint(self, name, params, data, method, headers):
    endpoint = self._endpoint(name)
    auth = self._auth()
    logger.debug("endpoint: {0}".format(endpoint))
    resp = method(endpoint, params = params, data = data, headers = headers, auth = auth)
    if resp.status_code != requests.codes.ok:
      raise Exception('API returned %s \nURL: %s\nParams: %s\nData sent: %s \nResponse text: %s' 
        % (resp.status_code, endpoint, params, data, resp.text))
    return resp

  def _endpoint(self, name = None):
    if name == None:
      return '%s' % (self.base_url)
    else:
      return '%s/%s' % (self.base_url, name)

  def _auth(self):
    #TODO: other authentication methods
    if self.user != None and self.password != None:
      return HTTPBasicAuth(self.user, self.password)

class NERService(WebService):
  def __init__(self, base_url):
    super(NERService, self).__init__(base_url)
    self.headers = {'Content-type': 'application/json'}

  def get_named_entities(self, data):
    resp = self._call_endpoint(None, None, data, requests.post, self.headers)
    j = resp.json()
    # Check if a confirmation parameter is there?
    return j;

# ElasticSearch API
class ElasticSearch(WebService):
  def __init__(self, base_url, user = None, password = None):
    super().__init__(base_url, user, password)
    
  def create_index(self, index_name, index_props):
    resp = self._call_endpoint(index_name, None, index_props, requests.put, None)
    j = resp.json()
    if not j['acknowledged']:
      raise Exception('Missing api acknowledge %s' % (resp.text))
    return j

  def delete_index(self, index_name):
    resp = self._call_endpoint(index_name, None, None, requests.delete, None)
    j = resp.json()
    if not j['acknowledged']:
      raise Exception('Missing api acknowledge %s' % (resp.text))
    return j

  def bulk(self, data):
    resp = self._call_endpoint('_bulk', None, data, requests.post, None)
    j = resp.json()
    logger.debug(j)
    if j['errors']:
      raise Exception('API reports errors %s' % (resp.text))
    return j
