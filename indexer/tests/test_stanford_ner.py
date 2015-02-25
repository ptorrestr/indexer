import unittest
import logging

from indexer.stanford_ner import StanfordCore
from indexer.logger import setup_logging

setup_logging()

logger = logging.getLogger('indexer')
logger.setLevel(logging.DEBUG)

sc = StanfordCore('http://localhost:3456')

text1 = 'this is an example text'
text2 = 'London is one of the most important cities in the world'

class TestStanfordCore(unittest.TestCase):
  def setUp(self):
    pass

  def test_get(self):
    r = sc.raw_parse(text1)
    self.assertGreater(len(r), 0)

  def test_get_named_entities(self):
    r = sc.get_named_entities(text2)
    self.assertGreater(len(r), 0)
