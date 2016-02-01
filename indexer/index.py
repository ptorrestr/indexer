import logging
import json 
import yaml
from concurrent.futures import ThreadPoolExecutor
from bz2 import BZ2File
from itertools import islice
from Queue import Queue

from indexer.wbservice import ElasticSearch
from indexer.stanford_ner import StanfordCore
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

def get_elastic_search_props():
  with open('etc/dbpedia_index.json') as data_file:
    data = data_file.read()
  return data
  
def create_package(index_header, contents):
  out = ""
  for content in contents:
    out += json.dumps(index_header) + "\n" + json.dumps(content) + "\n"
  return out

def triple_2_document(triple, dbpedia, stanford_core):
  if not "resource" in triple or not "predicate" in triple or not "object" in triple:
    raise Exception("Data is missing")
  uri = triple['resource']
  # set result in queue
  result_queue.put(dbpedia.index_concept(uri, stanford_core))

def triples_2_documents(triples, dbpedia, stanford_url, thread_num = 1):
  # create arrays for threads
  stanford_core = StanfordCore(stanford_url)
  # Run
  with ThreadPoolExecutor(max_workers = thread_num) as executor:
    for triple in triples:
      executor.submit(triple_2_document, triple, dbpedia, stanford_core)
  # get result
  documents = []
  while not result_queue.empty():
    documents.append(result_queue.get())
  return documents

def entry_2_triple(entry):
  return {'resource':entry[0], 'predicate':entry[1], 'object':entry[2] }

def index_triple(triples, index, index_header, dbpedia, stanford_url):
  docs = triples_2_documents(triples, dbpedia, stanford_url)
  data = create_package(index_header, docs)
  logger.debug(data)
  resp = index.bulk(data)
  logger.debug(resp)
  
def index_hdt(dbpedia_file_path, index, index_header, buffer_size, stanford_url):
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
        index_triple(triple_bag, index, index_header, dbpedia, stanford_url)
        logger.info("%i triples processed, %i triples indexed" 
          % ((total_lines + total_fail_lines), total_lines))
        triple_bag = []
      done.add(triple['resource'])
  if len(triple_bag) > 0:
    total_lines += len(triple_bag)
    index_triple(triple_bag, index, index_header, dbpedia, stanford_url)
    triple_bag = []
  logger.info("%iK triples indexed" % (total_lines/1000))
  logger.info("%iK triples failed" % (total_fail_lines/1000))
  logger.info("Done")
  return total_lines

def indexer(config, param):
  logger.info('Creating index %s on server %s' %(param.index_name, param.index_url))
  es = ElasticSearch(param.index_url)
  data = get_elastic_search_props()
  es.create_index(param.index_name, data)
  index_header = { "create" : { "_index": param.index_name, "_type": "triple" }}
  logger.info('Open hdt file %s' %(param.file_path))
  n = index_hdt(param.file_path, es, index_header, param.buffer_size, param.stanford_url)
