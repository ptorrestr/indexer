import unittest
import logging

from indexer.wbservice import ElasticSearch
from indexer.index import create_package
from indexer.index import get_elastic_search_props
from indexer.tests import ElasticSearchTestServer

logger = logging.getLogger(__file__)
index_props = get_elastic_search_props()

class TestElasticSearch(unittest.TestCase):
  def setUp(self):
    pass

  def test_client(self):
    with ElasticSearchTestServer(port = 9500) as ts:
      # Create index
      ES = ElasticSearch(ts.get_url())
      ES.create_index('test', index_props)
      # Bulk
      b_1 = { "index": { "_index": "test", "_type": "triple" }}
      s_1 = {"title":"myres1"}
      s_2 = {"title":"myres2"}
      contents = [s_1, s_2]
      data = create_package(b_1, contents)
      ES.bulk(data)
      # delete index
      ES.delete_index('test')
