import unittest
import logging

from indexer.wbservice import ElasticSearch
from indexer.index import create_package
from indexer.index import get_elastic_search_props

logger = logging.getLogger(__file__)
index_props = get_elastic_search_props()

class TestElasticSearch(unittest.TestCase):
  def setUp(self):
    pass

  def test_create_delete_index(self):
    ES = ElasticSearch('http://srvgal93:9200')
    ES.create_index('test', index_props)
    ES.delete_index('test') 

  def test_bulk(self):
    ES = ElasticSearch('http://srvgal93:9200')
    ES.create_index('test', index_props)
    b_1 = { "create": { "_index": "test", "_type": "triple" }}
    s_1 = {"title":"myres1"}
    s_2 = {"title":"myres2"}
    contents = [s_1, s_2]
    data = create_package(b_1, contents)
    ES.bulk(data)
    ES.delete_index('test')
