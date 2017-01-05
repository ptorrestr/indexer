import unittest
import logging

from t2db_objects import objects

from indexer.run import param_fields
from indexer.index import indexer
from indexer.wbservice import ElasticSearch
from indexer.utilities import create_bzip2_file
from indexer.utilities import create_hdt_file
from indexer.utilities import remove_file
from indexer.tests import ElasticSearchTestServer
from indexer.tests import NERTestServer

class TestRun(unittest.TestCase):
  def setUp(self):
    self.file_path = "etc/test.nt"
    self.bzip2_file_path = create_bzip2_file(self.file_path)
    self.hdt_file_path = create_hdt_file(self.bzip2_file_path, self.file_path)

  def tearDown(self):
    remove_file(self.bzip2_file_path)
    remove_file(self.hdt_file_path)

  def test_indexer(self):
    with ElasticSearchTestServer(port = 11534) as ests, NERTestServer(port = 11535) as nts:
      rawParams = {
        "index_url":ests.get_url(),
        "index_name":"test",
        "file_path":self.hdt_file_path,
        "buffer_size":10,
        "ner_url":nts.get_url(),
        "num_threads":1,
        "index_config":"etc/dbpedia_index.json",
      }
      params = objects.Configuration(param_fields, rawParams)
      indexer(None, params)
      es = ElasticSearch(params.index_url)
      es.delete_index(params.index_name)

      # With credentials
      rawParams["index_name"] = "test"
      rawParams["index_password"] = "test"
      params = objects.Configuration(param_fields, rawParams)
      indexer(None, params)
