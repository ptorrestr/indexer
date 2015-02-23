import logging
import argparse
import sys
import json

from t2db_objects import objects
from t2db_objects.utilities import readConfigFile2 as readConfigFile
from t2db_objects.utilities import formatHash

from indexer.logger import setup_logging
from indexer.index import index_hdt
from indexer.index import index_props
from indexer.wbservice import ElasticSearch

logger = logging.getLogger('indexer')

confFields = [
]

def getConfig(confFilePath):
  rawConfigNoFormat = readConfigFile(confFilePath)
  rawConfig = formatHash(rawConfigNoFormat, confFields)
  return objects.Configuration(confFields, rawConfig)

paramFields = [
  # Input parameters
  {"name":"index_url","kind":"mandatory","type":str,"default":None,"abbr":"--url","help":"ElasticSearch URL"},
  {"name":"index_name","kind":"mandatory","type":str,"default":None,"abbr":"--name","help":"Index name"},
  {"name":"file_path","kind":"mandatory","type":str,"default":None,"abbr":"--file","help":"the HDT file"},
  {"name":"buffer_size","kind":"non-mandatory","type":int,"default":100,"abbr":"--size","help":"Buffer size"},
]

def paramFields2parser(paramFields, description, epilog):
  #TODO validate parameter fields.
  parser = argparse.ArgumentParser(description = description, epilog = epilog)
  for parameter in paramFields:
    if parameter['default'] != None:
      parser.add_argument(
        parameter['abbr'],
        action = "store",
        dest = parameter['name'],
        help = parameter['help'],
        type = parameter['type'],
        default = parameter['default'],
        required = False)
    else:
      parser.add_argument(
        parameter['abbr'],
        action = "store",
        dest = parameter['name'],
        help = parameter['help'],
        type = parameter['type'],
        required = True)
  return parser.parse_args()

def parser2values(args, paramFields):
  rawParam = {}
  for parameter in paramFields:
    rawParam[parameter['name']] = getattr(args, parameter['name'])
  return rawParam

def runIndexer():
  setup_logging()

  # Read input
  description = 'Indexing HDT files on ElasticSearch'
  epilog = ''
  args = paramFields2parser(paramFields, description, epilog)
  rawParam = parser2values(args, paramFields)
  param = objects.Configuration(paramFields, rawParam)
  logger.info("Running")

  config = None

  indexer(config, param)
  logger.info("Finishing")
  sys.exit(0)

def indexer(config, param):
  es = ElasticSearch(param.index_url)
  es.create_index(param.index_name, json.dumps(index_props))
  index_header = { "create" : { "_index": param.index_name, "_type": "triple" }}
  n = index_hdt(param.file_path, es, index_header, param.buffer_size)
