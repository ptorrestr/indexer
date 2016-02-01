import unittest
import logging

from t2db_objects import objects

from indexer.run import param_fields
from indexer.index import indexer
from indexer.wbservice import ElasticSearch
from indexer.tests.test_index import create_bzip2_file
from indexer.tests.test_index import create_hdt_file
from indexer.tests.test_index import remove_file

class TestRun(unittest.TestCase):
  def setUp(self):
    pass

  #@unittest.skip("No processing")
  def test_indexer(self):
    file_path = "etc/test.nt"
    bzip2_file_path = create_bzip2_file(file_path)
    hdt_file_path = create_hdt_file(bzip2_file_path, file_path)
    rawParams = {
      "index_url":"http://srvgal93:9200",
      "index_name":"test",
      "file_path":hdt_file_path,
      "buffer_size":10,
      "ner_url":"http://srvgal80:8888/nee",
      "num_threads":1,
      "index_config":"etc/dbpedia_index.json",
    }
    params = objects.Configuration(param_fields, rawParams)
    indexer(None, params)
    es = ElasticSearch(params.index_url)
    es.delete_index(params.index_name)
    remove_file(bzip2_file_path)
    remove_file(hdt_file_path)
