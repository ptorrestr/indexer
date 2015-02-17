import requests
import json
import logging

logger = logging.getLogger('indexer')

headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}

def getRequest(url, data):
  r = requests.get(url, data = json.dumps(data), headers = headers)
  obj = json.loads(r.text)
  return obj

# ElasticSearch API
class ElasticSearch(object):
  def __init__(self, base_url):
    self.base_url = base_url

  def create_index(self, index_name, index_props):
    resp = self._call_endpoint(index_name, None, index_props, requests.put)
    j = resp.json()
    if not j['acknowledged']:
      raise Exception('Missing api acknowledge %s' % (resp.text))
    return j

  def delete_index(self, index_name):
    resp = self._call_endpoint(index_name, None, None, requests.delete)
    j = resp.json()
    if not j['acknowledged']:
      raise Exception('Missing api acknowledge %s' % (resp.text))
    return j

  def bulk(self, data):
    resp = self._call_endpoint('_bulk', None, data, requests.post)
    j = resp.json()
    logger.info(j)
    if j['errors']:
      raise Exception('API reports errors %s' % (resp.text))
    return j

  def _call_endpoint(self, name, params, data, method):
    endpoint = self._endpoint(name)
    resp = method(endpoint, params = params, data = data)
    if resp.status_code != requests.codes.ok:
      raise Exception('API returned %s : %s' % (resp.status_code, resp.text))
    return resp

  def _endpoint(self, name = None):
    if name == None:
      return '%s' % (self.base_url)
    else:
      return '%s/%s' % (self.base_url, name)

