import logging
import json
from bz2 import BZ2File
from itertools import islice

from indexer.wbservice import ElasticSearch

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
        "english_stop": {
          "type": "stop",
          "stopwords": "_english_"
        }
      },
      "analyzer": {
        "english": {
          "tokenizer":  "standard",
          "filter": [
            "lowercase",
            "english_stop"
          ]
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


def line2content(line):
  tokens = line.split()
  if len (tokens) < 3:
    raise Exception("Line has less than 3 tokens")
  if tokens[0] == '#':
    raise Exception("Line is a comment")
  return { "resource":tokens[0], "predicate":tokens[1], "object":tokens[2] }

def lines2contents(lines):
  contents = []
  for line in lines:
    try:
      content = line2content(line)
      contents.append(content)
    except Exception as e:
      logger.warning(e)
      continue
  return contents

def index_bzip2_file(file_path, index, index_header, buffer_size):
  logger.info("Reading file")
  try:
    bzip_file = Bzip2Reader(file_path, 'r', buffer_size)
    lines = bzip_file.nextLines()
    total_lines = 0
    while lines:
      contents = lines2contents(lines)
      data = create_package(index_header, contents)
      logger.debug(data)
      resp = index.bulk(data)
      logger.debug(resp)
      total_lines += len(lines)
      lines = bzip_file.nextLines()
    bzip_file.close()
  except Exception as e:
    logger.error("Failed while reading file")
    logger.error(e)
    raise e
  logger.info("Done")
  return total_lines
    
