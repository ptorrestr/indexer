import unittest
import logging

from indexer.wbservice import ElasticSearch
from indexer.index import create_package
from indexer.index import get_elastic_search_props
from indexer.tests import ElasticSearchTestServer

logger = logging.getLogger(__name__)

class TestElasticSearch(unittest.TestCase):
  def setUp(self):
    pass

  def test_client(self):
    with ElasticSearchTestServer(port = 11534) as ts:
      # Create index
      es = ElasticSearch(ts.get_url())
      logger.debug(es.base_url)
      es.create_index('test', get_elastic_search_props())
      # Bulk
      b_1 = { "index": { "_index": "test", "_type": "triple" }}
      s_1 = {"title":"myres1"}
      s_2 = {"title":"myres2"}
      contents = [s_1, s_2]
      data = create_package(b_1, contents)
      es.bulk(data)
      # delete index
      es.delete_index('test')
