import unittest
import logging
import json

from indexer.wbservice import ElasticSearch
from indexer.logger import setup_logging
from indexer.index import create_package
from indexer.index import index_props
from indexer.index import lines2contents

logger = logging.getLogger('indexer')
logger.setLevel(logging.DEBUG)

setup_logging()

class TestElasticSearch(unittest.TestCase):
  def setUp(self):
    pass

  def test_create_delete_index(self):
    ES = ElasticSearch('http://localhost:9200')
    ES.create_index('test', json.dumps(index_props))
    ES.delete_index('test') 

  def test_bulk(self):
    ES = ElasticSearch('http://localhost:9200')
    ES.create_index('test', json.dumps(index_props))
    b_1 = { "create": { "_index": "test", "_type": "triple" }}
    s_1 = "myres\tmypre\tmyobj"
    s_2 = "myres1\tmypre1\tmyobj1"
    lines = [s_1, s_2]
    contents = lines2contents(lines)
    data = create_package(b_1, contents)
    ES.bulk(data)
    ES.delete_index('test')
