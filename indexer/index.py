import logging
import json 
import yaml
from concurrent.futures import ThreadPoolExecutor
from bz2 import BZ2File
from itertools import islice

from indexer.wbservice import ElasticSearch
from indexer.stanford_ner import StanfordCore
from indexer.dbpedia import DBpedia

logger = logging.getLogger(__name__)

class Bzip2Reader(BZ2File):
  def __init__(self, filename, mode='r', buffer_size = 100):
    self.buffer_size = buffer_size
    super(Bzip2Reader, self).__init__(filename, mode)

  def nextLines(self):
    nextLines = list(islice(self, self.buffer_size))
    return self.bytes2str(nextLines)

  def bytes2str(self, lines):
    return [ line.decode("utf-8") for line in lines ]
  
def create_package(index_header, contents):
  out = ""
  for content in contents:
    out += json.dumps(index_header) + "\n" + json.dumps(content) + "\n"
  return out

def triple_2_document(triple, dbpedia, stanford_core):
  if not "resource" in triple or not "predicate" in triple or not "object" in triple:
    raise Exception("Data is missing")
  uri = triple['resource']
  doc = dbpedia.index_concept(uri)
  return doc

def _triples_2_documents(triples, dbpedia, stanford_url):
  stanford_core = StanfordCore(stanford_url)
  documents = []
  for triple in triples:
    documents.append(triple_2_document(triple, dbpedia, stanford_core))
  return documents

def triples_2_documents(triples, dbpedia, stanford_url, thread_num = 1):
  triples_per_thread = []
  # create arrays for threads
  output_thread = []
  base_url = "http://localhost"
  port= 3455
  stanford_url = []
  for j in range(0, thread_num):
    triples_per_thread.append([])
    output_thread.append([]) 
    stanford_url.append("%s:%i" % (base_url,port))

  # split data through threads
  for i in range(0, len(triples)):
    thread_id = i % thread_num
    triples_per_thread[thread_id].append(triples[i])

  # Create structure for thread result
  documents = []

  # Run
  with ThreadPoolExecutor(max_workers = 8) as executor:
    for j in range(0, thread_num):
      output_thread[j] = executor.submit(_triples_2_documents, triples_per_thread[j], dbpedia, stanford_url[j])
  # Merge result
  for output in output_thread:
    documents.extend(output.result())
    
  #for triple in triples:
  #  documents.append(triple2document(triple, hdt, stanford_core))
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
  try:
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
      logger.info('next')
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
          logger.info("%.2fK lines processed, %.2fK lines indexed" % ((total_lines + total_fail_lines)/1000, total_lines/1000))
          triple_bag = []
        done.add(triple['resource'])
    if len(triple_bag) > 0:
      total_lines += len(triple_bag)
      index_triple(triple_bag, index, index_header, dbpedia, stanford_url)
      triple_bag = []
    logger.info("%iK lines indexed" % (total_lines/1000))
    logger.info("%iK lines failed" % (total_fail_lines/1000))
    
  except Exception as e:
    logger.error("Failed while reading HDT file")
    logger.error(e)
    raise e
  logger.info("Done")
  return total_lines

def indexer(config, param):
  logger.info('Creating index %s on server %s' %(param.index_name, param.index_url))
  es = ElasticSearch(param.index_url)
  with open('etc/dbpedia_index2.json') as data_file:    
    data = data_file.read()
  es.create_index(param.index_name, data)
  index_header = { "create" : { "_index": param.index_name, "_type": "triple" }}
  logger.info('Open hdt file %s' %(param.file_path))
  n = index_hdt(param.file_path, es, index_header, param.buffer_size, param.stanford_url)
