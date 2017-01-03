import unittest
import logging
import json
import subprocess
import os.path

from indexer.index import Bzip2Reader
from indexer.index import index_hdt
from indexer.index import get_elastic_search_props
from indexer.wbservice import ElasticSearch
from indexer.tests import ElasticSearchTestServer
from indexer.tests import ner_server

logger = logging.getLogger(__file__)

def create_bzip2_file(file_path):
  if not os.path.isfile(file_path + ".tmp.bz2"): 
    subprocess.call(["cp", file_path, file_path + ".tmp"])
    subprocess.call(["bzip2", file_path + ".tmp"])
  return file_path + ".tmp.bz2"

def create_hdt_file(input_file_path, output_file_path):
  if not os.path.isfile(output_file_path + ".hdt"):
    subprocess.call(["rdf2hdt", input_file_path, output_file_path + ".hdt"])
  return output_file_path + ".hdt"

def remove_file(file_path):
  if os.path.isfile(file_path):
    subprocess.call(["rm", file_path])

class TestBzip2Reader(unittest.TestCase):
  def setUp(self):
    pass

  def test_nextLines(self):
    file_path = "etc/test.nt"
    bzip2_file_path = create_bzip2_file(file_path)
    totalLines = 0
    try:
      f = Bzip2Reader(bzip2_file_path, "r", 10)
      lines = f.nextLines()
      totalLines = len(lines)
      while lines :
        lines = f.nextLines()
        totalLines += len(lines)
      f.close()
    except Exception as e:
      logger.error("Exception while reading")
      logger.error(e)
    remove_file(bzip2_file_path)
    self.assertEqual(totalLines, 100) 

#@unittest.skip("No processing")
class TestIndexer(unittest.TestCase):
  def setUp(self):
    pass

  def test_index_hdt(self):
    file_path = "etc/test.nt"
    index_name = "test"
    index_header = { "create" : { "_index": index_name, "_type": "triple" }}
    buffer_size = 10
    num_threads = 1
    try:
      with ElasticSearchTestServer(port = 9500) as ests:
        bzip2_file_path = create_bzip2_file(file_path)
        hdt_file_path = create_hdt_file(bzip2_file_path, file_path)
        es = ElasticSearch(ests.get_url())
        es.create_index(index_name, get_elastic_search_props() )
        n = index_hdt(hdt_file_path, es, index_header, buffer_size, ner_server, num_threads)
        es.delete_index(index_name)
        remove_file(bzip2_file_path)
        remove_file(hdt_file_path)
    except Exception as e:
      logger.error(e)
    self.assertEqual(19, n)
    
