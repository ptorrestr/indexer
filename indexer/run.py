import logging
import argparse
import sys
import json

from t2db_objects.parameters import generate_parameters
from t2db_objects.logger import setup_logging

from indexer.index import indexer

logger = logging.getLogger(__name__)

conf_fields = [
]

param_fields = [
  # Input parameters
  {"name":"index_url","kind":"mandatory","type":str,"default":None,"abbr":"--url","help":"ElasticSearch URL"},
  {"name":"index_user","kind":"non-mandatory","type":str,"default":"","abbr":"--user","help":"ElasticSearch username"},
  {"name":"index_password", "kind":"non-mandatory","type":str,"default":"","abbr":"--password","help":"ElasticSearch user password"},
  {"name":"index_name","kind":"mandatory","type":str,"default":None,"abbr":"--name","help":"Index name"},
  {"name":"file_path","kind":"mandatory","type":str,"default":None,"abbr":"--file","help":"the HDT file"},
  {"name":"buffer_size","kind":"non-mandatory","type":int,"default":100,"abbr":"--size","help":"Buffer size"},
  {"name":"ner_url","kind":"mandatory","type":str,"default":None,"abbr":"--ner-url","help":"The Stanford NER URL"},
  {"name":"num_threads","kind":"non-mandatory","type":int,"default":1,"abbr":"--num-threads","help":"Number of threads"},
  {"name":"index_config","kind":"mandatory","type":str,"default":None,"abbr":"--index-config","help":"ElasticSearch configuration file"},
]

def runIndexer():
  setup_logging()
  
  # Read input
  description = 'Indexing HDT files on ElasticSearch'
  epilog = 'Pablo Torres, pablo.torres@insight-centre.org'
  param = generate_parameters(param_fields, description, epilog)
  config = None
  logger.info("Running")
  indexer(config, param)
  logger.info("Finishing")
  sys.exit(0)
