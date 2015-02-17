import unittest
import logging
import json
import subprocess
import os.path

from indexer.index import Bzip2Reader
from indexer.index import index_bzip2_file
from indexer.index import index_props
from indexer.wbservice import ElasticSearch
from indexer.logger import setup_logging

setup_logging()

logger = logging.getLogger('indexer')
logger.setLevel(logging.DEBUG)

def create_bzip2_file(file_path):
  if not os.path.isfile(file_path + ".tmp.bz2"): 
    subprocess.call(["cp", file_path, file_path + ".tmp"])
    subprocess.call(["bzip2", file_path + ".tmp"])
  return file_path + ".tmp.bz2"

def remove_file(file_path):
  if os.path.isfile(file_path):
    subprocess.call(["rm", file_path])

class TestBzip2Reader(unittest.TestCase):
  def setUp(self):
    pass

  def test_nextLines(self):
    file_path = "etc/test.dat"
    bzip2_file_path = create_bzip2_file(file_path)
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

class TestIndexer(unittest.TestCase):
  def setUp(self):
    pass

  def test_index_bzip2_file(self):
    file_path = "etc/test.dat"
    index_uri = "http://localhost:9200"
    index_name = "test"
    index_header = { "create" : { "_index": index_name, "_type": "triple" }}
    buffer_size = 10
    bzip2_file_path = create_bzip2_file(file_path)
    es = ElasticSearch(index_uri)
    es.create_index(index_name, json.dumps(index_props))
    n = index_bzip2_file(bzip2_file_path, es, index_header, buffer_size)
    es.delete_index(index_name)
    remove_file(bzip2_file_path)
    self.assertEqual(100, n)
    
