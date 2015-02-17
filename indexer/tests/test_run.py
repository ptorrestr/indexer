import unittest
import logging

from t2db_objects import objects

from indexer.run import paramFields
from indexer.run import indexer
from indexer.logger import setup_logging
from indexer.tests.test_index import create_bzip2_file
from indexer.tests.test_index import remove_file

setup_logging()
logger = logging.getLogger('indexer')
logger.setLevel(logging.DEBUG)

class TestRun(unittest.TestCase):
  def setUp(self):
    pass

  def test_indexer(self):
    bzip2_file_path = create_bzip2_file("etc/test.dat")
    rawParams = {
      "index_url":"http://localhost:9200",
      "index_name":"test",
      "file_path":bzip2_file_path,
    }
    params = objects.Configuration(paramFields, rawParams)
    remove_file(bzip2_file_path)
