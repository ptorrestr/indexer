import logging

import stanford
from corenlp import StanfordCoreNLP

logger = logging.getLogger('indexer')

# Singleton variable.
stanford_core_inst = None

class StanfordCore(object):
  def __init__(self, stanford_path = None):
    # if not stanford path is given, we use default path.
    if not stanford_path:
      stanford_path = stanford.get_path()
    global stanford_core_inst
    if not stanford_core_inst:
      logger.info("Loading Stanford Core: %s" %(stanford_path))
      stanford_core_inst = StanfordCoreNLP(stanford_path)
      logger.info("Done")
    self.stanford_core = stanford_core_inst

  def raw_parse(self, text):
    return self.stanford_core.raw_parse(text)

  def get_named_entities(self, text):
    if text  == None or len(text) <= 0:
      raise Exception("Text is not defined")
    named_entities = set()
    document = self.raw_parse(text)
    sentences = document['sentences']
    for sentence in sentences :
      current_ner = ""
      for word, content in sentence['words']:
        named_entity_annot = content['NamedEntityTag']
        if not named_entity_annot == "O":
          current_ner += " " + word
        else:
          if not current_ner == "":
            named_entities.add(current_ner)
            current_ner = ""
      if not current_ner == "":
        named_entities.add(current_ner)
    return named_entities

