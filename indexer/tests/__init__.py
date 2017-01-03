import requests
import os
import sys
import hashlib
import logging
import tarfile
import time
import subprocess
from subprocess import call
from tqdm import tqdm

from t2db_objects.logger import setup_logging
from t2db_objects.utilities import read_env_variable

setup_logging('etc/logging_debug.yaml')
logger = logging.getLogger(__file__)
es_server = read_env_variable('ELASTICSEARCH_DEV_URL')
ner_server = read_env_variable('NER_DEV_URL')
BUFFER = 1024
base_path = "/tmp/indexer_1/"
filename = "elasticsearch-5.1.1" 
zip_extension = ".tar.gz"
url_base = "https://artifacts.elastic.co/downloads/elasticsearch/"

class ElasticSearch(object):
  def __init__(self):
    self.base_path = "/tmp/indexer_1/"
    self.filename = "elasticsearch-5.1.1" 
    self.zip_extension = ".tar.gz"
    self.url_base = "https://artifacts.elastic.co/downloads/elasticsearch/"

  def start(self):
    if not os.path.exists(self.base_path):
      os.makedirs(self.base_path)
    if not os.path.isfile(self.base_path + self.filename + self.zip_extension):
      download_file(self.filename + self.zip_extension, self.url_base, self.base_path, sha1 = self.filename + ".sha1")
    if not os.path.exists(self.base_path + self.filename):
      unzip(self.base_path + self.filename + self.zip_extension, self.base_path)

    cmd_start = [
      self.base_path + self.filename + "/bin/elasticsearch",
      "--pidfile=" + self.base_path + "server.pid",
      "-d",
    ]
    call(cmd_start, cwd = self.base_path)
    time.sleep(5)

  def stop(self):
    with open(self.base_path + "server.pid") as f:
      pid = f.read()
    cmd_stop = [
      "/bin/bash",
      "-c",
      "kill -9 " + pid,
    ]
    call(cmd_stop, cwd = self.base_path)
    cmd_clean = [
      "/bin/bash",
      "-c",
      "rm -rf " + self.base_path + self.filename + "/data",
    ]
    call(cmd_clean, cwd = self.base_path)

def download_file(filename, url_base, output_path, sha1 = None, md5 = None):
  # Download file
  data1 = url_base + filename
  r = requests.get(data1, stream=True)
  p = r.headers['content-length']
  total = int(p) / BUFFER
  if r.status_code == 200:
    with open(output_path + filename, 'wb') as f:
      for chunk in tqdm(r.iter_content(BUFFER), total = total):
        f.write(chunk)
  # Verify hash
  if sha1 or md5:
    if sha1:
      data2 = url_base + sha1
    if md5:
      data2 = url_base + md5
    r = requests.get(data2)
    if r.status_code == 200:
      true_hash = r.text
    hash_ = compute_hash(output_path + filename, md5 = md5, sha1 = sha1)
    if hash_.hexdigest() == true_hash:
      logger.info("Verified")
    else:
      logger.info("Hash verification failed")
  logger.info("Download successfull")

def compute_hash(path, md5 = None, sha1 = None):
  if md5:
    hash_ = hashlib.md5()
  elif sha1:
    hash_ = hashlib.sha1()
  else:
    raise Exception("No hash defined")
  with open(path, 'rb') as f:
    while True:
      data = f.read(BUFFER)
      if not data:
          break
      hash_.update(data)
  return hash_

def unzip(filepath, output_path):
  with tarfile.open(filepath) as f:
    f.extractall(path = output_path)

