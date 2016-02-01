import logging
import json 
import yaml
from concurrent.futures import ThreadPoolExecutor
from bz2 import BZ2File
from itertools import islice
from Queue import Queue

from indexer.wbservice import ElasticSearch
from indexer.wbservice import NERService
from indexer.dbpedia import DBpedia

logger = logging.getLogger(__name__)

result_queue = Queue()

class Bzip2Reader(BZ2File):
  def __init__(self, filename, mode='r', buffer_size = 100):
    self.buffer_size = buffer_size
    super(Bzip2Reader, self).__init__(filename, mode)

  def nextLines(self):
    nextLines = list(islice(self, self.buffer_size))
    return self.bytes2str(nextLines)

  def bytes2str(self, lines):
    return [ line.decode("utf-8") for line in lines ]

def get_elastic_search_props( file_path = 'etc/dbpedia_index.json'):
  with open(file_path) as data_file:
    data = data_file.read()
  return data
  
def create_package(index_header, contents):
  out = ""
  for content in contents:
    out += json.dumps(index_header) + "\n" + json.dumps(content) + "\n"
  return out

def triple_2_document(triple, dbpedia, ner_core):
  if not "resource" in triple or not "predicate" in triple or not "object" in triple:
    raise Exception("Data is missing")
  uri = triple['resource']
  # set result in queue
  result_queue.put(dbpedia.index_concept(uri, ner_core))

def triples_2_documents(triples, dbpedia, ner_url, num_threads = 2):
  # create arrays for threads
  ner_core = NERService(ner_url)
  # Run
  with ThreadPoolExecutor(max_workers = num_threads) as executor:
    for triple in triples:
      executor.submit(triple_2_document, triple, dbpedia, ner_core)
  # get result
  documents = []
  while not result_queue.empty():
    documents.append(result_queue.get())
  return documents

def entry_2_triple(entry):
  return {'resource':entry[0], 'predicate':entry[1], 'object':entry[2] }

def index_triple(triples, index, index_header, dbpedia, ner_url, num_threads):
  docs = triples_2_documents(triples, dbpedia, ner_url, num_threads)
  data = create_package(index_header, docs)
  logger.debug(data)
  resp = index.bulk(data)
  logger.debug(resp)
  
def index_hdt(dbpedia_file_path, index, index_header, buffer_size, ner_url, num_threads):
  logger.info("Reading HDT file")
  dbpedia = DBpedia(dbpedia_file_path)
  # Get all triples
  it = dbpedia.search("", "", "")
  done = set()
  triple_bag = []
  total_lines = 0
  total_fail_lines = 0
  while it.has_next():
    dbpedia_entry = it.next()
    triple =  entry_2_triple(dbpedia_entry)
    if triple['resource'] in done:
      logger.debug( "%s: already indexed" % triple['resource'])
      total_fail_lines += 1
      continue
    if dbpedia.is_redirect(triple['resource']):
      logger.debug( "%s: is redirect" % triple['resource'])
      total_fail_lines += 1
      continue
    else:
      logger.debug("adding to bug")
      triple_bag.append(triple)
      if len(triple_bag) >= buffer_size:
        total_lines += buffer_size
        index_triple(triple_bag, index, index_header, dbpedia, ner_url, num_threads)
        logger.info("%i triples processed, %i triples indexed" 
          % ((total_lines + total_fail_lines), total_lines))
        triple_bag = []
      done.add(triple['resource'])
  if len(triple_bag) > 0:
    total_lines += len(triple_bag)
    index_triple(triple_bag, index, index_header, dbpedia, ner_url, num_threads)
    triple_bag = []
  logger.info("%iK triples indexed" % (total_lines/1000))
  logger.info("%iK triples failed" % (total_fail_lines/1000))
  logger.info("Done")
  return total_lines

def indexer(config, param):
  logger.info('Creating index %s on server %s' %(param.index_name, param.index_url))
  es = ElasticSearch(param.index_url)
  logger.info('Using file: %s' % param.index_config)
  data = get_elastic_search_props(param.index_config)
  es.create_index(param.index_name, data)
  index_header = { "create" : { "_index": param.index_name, "_type": "triple" }}
  logger.info('Threads available: %i' %( param.num_threads))
  logger.info('Open hdt file %s' %(param.file_path))
  n = index_hdt(param.file_path, es, index_header, param.buffer_size, param.ner_url, param.num_threads)
