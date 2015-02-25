import logging
import jsonrpclib
import json

logger = logging.getLogger('indexer')

class StanfordCore(object):
  def __init__(self, stanford_url):
    logger.info("Loading Stanford Core: %s" %(stanford_url))
    self.stanford_core = jsonrpclib.Server(stanford_url)
    logger.info("Done")

  def raw_parse(self, text):
    return json.loads(self.stanford_core.parse(text))

  def get_named_entities(self, text):
    if text  == None or len(text) <= 0:
      raise Exception("Text is not defined")
    named_entities = set()
    document = self.raw_parse(text)
    sentences = document['sentences']
    for sentence in sentences :
      current_ner = ""
      for word, content in sentence['words']:
        if not 'NamedEntityTag' in content:
          logger.warning("No namedEntityTag found on")
          logger.warning("Sentence: %s" % sentence)
          logger.worning("Word: %s" %word)
          continue
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

