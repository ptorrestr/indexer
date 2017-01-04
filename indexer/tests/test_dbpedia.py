import unittest
import logging
import os
import subprocess

from indexer.utilities import create_bzip2_file
from indexer.utilities import create_hdt_file
from indexer.utilities import remove_file
from indexer.dbpedia import DBpedia

logger = logging.getLogger(__name__)

class TestDBpedia(unittest.TestCase):
  def setUp(self):
    self.file_path = "etc/test.nt"
    self.bzip2_file_path = create_bzip2_file(self.file_path)
    self.hdt_file_path = create_hdt_file(self.bzip2_file_path, self.file_path)
    self.c = DBpedia(self.hdt_file_path)

  def tearDown(self):
    remove_file(self.bzip2_file_path)
    remove_file(self.hdt_file_path)

  def test_dbpedia_init(self):
    it = self.c.search("", "", "")
    while it.has_next():
      logger.info(it.next())

  def test_dbpedia_funcs(self):
    resource = 'http://dbpedia.org/ontology/'
    res1 = self.c.get_definition(resource)
    # TODO: Get a better nt file in order to do the rest of the test. 
    # Current file does not have any of these relationships.

    #self.assertIsNotNone(res1)
    #res2 = self.c.get_is_redirect(resource, resource)
    #self.assertFalse(res2)
    #res3 = self.c.get_dbpedia_categories_of_res(resource)
    #self.assertFalse(res3)
    #res4 = self.c.get_dbpedia_classes_of_res(resource)
    #self.assertIsNotNone(res4)
    #res5 = self.c.get_dbpedia_labels(resource)
    #res6 = self.c.disambiguation_pages(resource)
    #res = self.c.get_ambigous_page(resource)
    #res = self.c.select_rdfs_comment_of_resource(resource)
    #res = self.c.is_disambiguation_page(resource)
    #res = self.c.select_redirected_pages_to(resource)
    #res = self.c.select_dbpedia_url_of_title("ontology")
    #res = self.c.get_dbpedia_url_for_title("ontology")
    #res = self.c.is_redirect(resource)

