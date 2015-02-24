import logging
import json 
from bz2 import BZ2File
from itertools import islice

from hdt import dbpedia
from indexer.wbservice import ElasticSearch
from indexer.stanford_ner import StanfordCore
from indexer import utils

logger = logging.getLogger('indexer')

class Bzip2Reader(BZ2File):
  def __init__(self, filename, mode='r', buffer_size = 100):
    self.buffer_size = buffer_size
    super(Bzip2Reader, self).__init__(filename, mode)

  def nextLines(self):
    nextLines = list(islice(self, self.buffer_size))
    return self.bytes2str(nextLines)

  def bytes2str(self, lines):
    return [ line.decode("utf-8") for line in lines ]
  
index_props = {
  "settings": {
    "index": {
      "number_of_shards": 3,
      "number_of_replicas": 0,
    },
    "analysis": {
      "filter": {
        "english_stop" : {
          "type": "stop",
          "stopwords": "_english_",
        }
      },
      "analyzer": {
        "safe_keyword_analyzer": {
          "tokenizer": "keyword",
        },
        "stopword_keyword_analyzer": {
          "tokenizer": "whitespace",
          "filter": ["lowercase", "english_stop", "porter_stem"],
        },
        "lemma_standard_analyzer": {
          "tokenizer": "standard",
          "filter": ["standard", "lowercase", "english_stop", "porter_stem"],
        },
      }
    }
  },
  "mappings": {
    "triple": {
      "properties": {
        "title": {
          "type": "string",
          "analyzer": "safe_keyword_analyzer",
          "store" : True,
          "copy_to" : [
            "title_lowcase_lemma_stopwords", 
            "title_text",
            "title_text_lemma",
          ]
        },
        # META
        "title_lowcase_lemma_stopwords" : {
          "type": "string",
          "analyzer": "stopword_keyword_analyzer",
          "store" : True,
        },
        # META
        "title_text" : {
          "type": "string",
          "store" : True,
        },
        # META
        "title_text_lemma": {
          "type": "string",
          "analyzer": "lemma_standard_analyzer",
          "store" : True,
        },
        "redir_title": {
          "type": "string",
          "analyzer": "safe_keyword_analyzer",
          "store": True,
          "copy_to" : [
            "redir_title_lowcase_lemma_stopwords", 
            "redir_title_text",
            "redirect_title_text_lemma",
          ]
        },
        # META
        "redir_title_lowcase_lemma_stopwords": {
          "type": "string",
          "analyzer": "stopword_keyword_analyzer",
          "store": True,
        },
        # META
        "redir_title_text": {
          "type": "string",
          "store": True,
        },
        # META
        "redirect_title_text_lemma": {
          "type": "string",
          "analyzer": "lemma_standard_analyzer",
          "store": True,
        },
        "dbpedia_page": {
          "type": "string",
          "analyzer": "safe_keyword_analyzer",
          "store" : True,
        },
        "dbpedia_redir_page": {
          "type": "string",
          "analyzer": "safe_keyword_analyzer",
          "store" : True,
        },
        "rdfs_comment": {
          "type": "string",
          "term_vector": "with_positions_offsets_payloads",
          "store" : True,
        },
        "rdfs_comment_named_entities": {
          "type": "string",
          "store" : True,
          "indexed" : False,
        },
        "is_disambiguation_page": {
          "type": "boolean",
          "store" : True,
          "indexed" : False,
        },
        "disambiguates_to": {
          "type" : "string",
          "store" : True,
          "indexed" : False,
        },
        "ambiguous_page": {
          "type" : "string",
          "store" : True,
          "indexed" : False,
        },
        "is_disambiguation_result_page": {
          "type" : "boolean",
          "store" : True,
          "indexed" : False,
        },
        "resource": {
          "type": "string",
          "index": "not_analyzed"
        },
        "predicate": {
          "type": "string",
          "index": "not_analyzed"
        },
        "object": {
          "type": "string",
          "index": "not_analyzed"
        }
      }
    }
  }
  
}

def create_package(index_header, contents):
  out = ""
  for content in contents:
    out += json.dumps(index_header) + "\n" + json.dumps(content) + "\n"
  return out

def triple2document(triple, hdt, stanford_core):
  if not "resource" in triple or not "predicate" in triple or not "object" in triple:
    raise Exception("Data is missing")
  uri = triple['resource']
  logger.info(uri)
  title = utils.get_title_from_dbpedia_url(uri)
  rdfs_comment = hdt.select_rdfs_comment_of_resource(uri)
  rdfs_comment_named_entities = []
  if rdfs_comment :
    logger.info(rdfs_comment)
    rdfs_comment_named_entities = stanford_core.get_named_entities(rdfs_comment)
    # We transform the sets since sets are not json callable
    rdfs_comment_named_entities = list(rdfs_comment_named_entities)
    logger.info("stanford end")

  # base doc
  doc = {
    "title": title,
    "dbpedia_page": uri,
    "rdfs_comment": rdfs_comment,
    "rdfs_comment_named_entities": rdfs_comment_named_entities,
  }
  
  redirected_pages = hdt.select_redirected_pages_to(uri)
  if redirected_pages and len(redirected_pages) > 0:
    redir_title = utils.get_titles_from_dbpedia_urls(redirected_pages)
    # We transform the sets since sets are not json callable
    doc['redir_title'] = list(redir_title)
    doc['dbpedia_redir_page'] = list(redirected_pages)

  disambiguates_to = hdt.disambiguation_pages(uri)
  is_disambiguation_page = True if disambiguates_to and len(disambiguates_to) > 0 else False
  doc['is_disambiguation_page'] = is_disambiguation_page
  if is_disambiguation_page:
    # We transform the disambiguates_to set since sets are not json callable
    doc['disambiguates_to'] = list(disambiguates_to)

  ambiguous_page = hdt.get_ambigous_page(uri)
  is_disambiguation_result_page = True if ambiguous_page else False
  doc['is_disambiguation_result_page'] = is_disambiguation_result_page
  if is_disambiguation_result_page: 
    doc['ambiguous_page'] = ambiguous_page

  logger.info("Doc ready")
  return doc

def triples2documents(triples, hdt, stanford_core):
  documents = []
  for triple in triples:
    documents.append(triple2document(triple, hdt, stanford_core))
  return documents

def hdt2triple(triple_hdt):
  return {'resource':triple_hdt[0], 'predicate':triple_hdt[1], 'object':triple_hdt[2] }

def index_concept(triples, index, index_header, hdt, stanford_core):
  docs = triples2documents(triples, hdt, stanford_core)
  data = create_package(index_header, docs)
  resp = index.bulk(data)
  logger.debug(data)
  
  
def index_hdt(file_path, index, index_header, buffer_size):
  stanford_core = StanfordCore()
  logger.info("Reading HDT file")
  try:
    hdt = dbpedia.DBpedia(file_path)
    # Get all triples
    it = hdt.search("", "", "")
    done = set()
    triple_bag = []
    total_lines = 0
    total_fail_lines = 0
    while it.has_next():
      triple_hdt = it.next()
      triple =  hdt2triple(triple_hdt)
      if triple['resource'] in done:
        logger.debug( "%s: already indexed" % triple['resource'])
        total_fail_lines += 1
        continue
      if hdt.is_redirect(triple['resource']):
        logger.debug( "%s: is redirect" % triple['resource'])
        total_fail_lines += 1
        continue
      else:
        triple_bag.append(triple)
        if len(triple_bag) >= buffer_size:
          total_lines += buffer_size
          index_concept(triple_bag, index, index_header, hdt, stanford_core)
          logger.info("%iK lines indexed" % (total_lines/1000))
          triple_bag = []
        done.add(triple['resource'])
    if len(triple_bag) > 0:
      total_lines += len(triple_bag)
      index_concept(triple_bag, index, index_header, hdt, stanford_core)
      triple_bag = []
    logger.info("%i lines indexed" % (total_lines))
    logger.info("%i lines failed" % (total_fail_lines))
    
  except Exception as e:
    logger.error("Failed while reading HDT file")
    logger.error(e)
    raise e
  logger.info("Done")
  return total_lines

