import unittest
import logging
import json
import subprocess
import os.path

from indexer.utilities import create_bzip2_file
from indexer.utilities import create_hdt_file
from indexer.utilities import remove_file
from indexer.index import Bzip2Reader
from indexer.index import index_hdt
from indexer.index import get_elastic_search_props
from indexer.wbservice import ElasticSearch
from indexer.tests import ElasticSearchTestServer
from indexer.tests import NERTestServer

logger = logging.getLogger(__name__)

class TestIndexer(unittest.TestCase):
  def setUp(self):
    self.file_path = "etc/test.nt"
    self.bzip2_file_path = create_bzip2_file(self.file_path)
    self.hdt_file_path = create_hdt_file(self.bzip2_file_path, self.file_path)

  def tearDown(self):
    remove_file(self.bzip2_file_path)
    remove_file(self.hdt_file_path)

  def test_bzip2_reader(self):
    totalLines = 0
    try:
      f = Bzip2Reader(self.bzip2_file_path, "r", 10)
      lines = f.nextLines()
      totalLines = len(lines)
      while lines :
        lines = f.nextLines()
        totalLines += len(lines)
      f.close()
    except Exception as e:
      logger.error("Exception while reading")
      logger.error(e)
    self.assertEqual(totalLines, 100) 

  def test_index_hdt(self):
    index_name = "test"
    index_header = { "index" : { "_index": index_name, "_type": "triple" }}
    buffer_size = 10
    num_threads = 1
    with ElasticSearchTestServer(port = 11534) as ests, NERTestServer(port = 11535) as nts:
      es = ElasticSearch(ests.get_url())
      es.create_index(index_name, get_elastic_search_props() )
      n = index_hdt(self.hdt_file_path, es, index_header, buffer_size, nts.get_url(), num_threads)
      es.delete_index(index_name)
    self.assertEqual(19, n)
    
