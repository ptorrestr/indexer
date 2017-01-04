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
logger = logging.getLogger(__name__)

class TestServer(object):
  def __init__(self, base_path, filename, zip_extension, url_base, port, hash_extension, cmd_start, cmd_clean = None):
    self.base_path = base_path
    self.filename = filename
    self.zip_extension = zip_extension
    self.url_base = url_base
    self.port = str(port)
    self.hash_extension = hash_extension
    self.cmd_start = cmd_start
    self.cmd_clean = cmd_clean

  def __enter__(self):
    if not os.path.exists(self.base_path):
      os.makedirs(self.base_path)
    if not os.path.isfile(self.base_path + self.filename + self.zip_extension):
      if self.hash_extension:
        download_file(self.filename + self.zip_extension, self.url_base, self.base_path, sha1 = self.filename + hash_extension)
      else:
        download_file(self.filename + self.zip_extension, self.url_base, self.base_path)
    if not os.path.exists(self.base_path + self.filename):
      unzip(self.base_path + self.filename + self.zip_extension, self.base_path)
    self._start()
    self._test()
    return self

  def __exit__(self, exc_type, exc_value, traceback):
    # TODO check trace and errors
    self._stop()
    self._clean()

  def _start(self):
    logger.info("Starting {0}".format(self.filename))
    self.proc = subprocess.Popen(self.cmd_start, cwd = self.base_path + self.filename, 
      stdout = subprocess.DEVNULL, stderr = subprocess.DEVNULL, stdin = subprocess.DEVNULL)

  def _test(self):
    pass

  def _stop(self):
    logger.info("Stopping {0}".format(self.filename))
    self.proc.kill()

  def _clean(self):
    if self.cmd_clean:
      clean = subprocess.Popen(self.cmd_clean, cwd = self.base_path + self.filename)
      clean.wait()

  def get_url(self):
    return "http://localhost:" + self.port

class NERTestServer(TestServer):
  def __init__(self, port = 8200):
    base_path = "/tmp/ner_1/"
    filename = "neel2016-nee-servlet-dda1ce83848c6c0dc6e3e436e0be4a2f183b5742"
    zip_extension = ".tar.gz"
    url_base = "http://srvgal80.deri.ie/~pabtor/"
    hash_extension = None
    cmd_start = [
      "/bin/bash",
      "-c",
      "mvn -Djetty.http.port=" + str(port) + " jetty:run",
    ]
    super(NERTestServer, self).__init__(base_path, filename, zip_extension, url_base, port, hash_extension, cmd_start)

  def get_url(self):
    #TODO: we have to add the path since it's hard coded in the NER code. This should be changed!
    return "http://localhost:" + self.port + "/nee"

  def _test(self):
    for i in range(0, 30):
      time.sleep(2)
      try:
        resp = requests.get(self.get_url())
        print(resp.status_code)
        if resp.status_code > 200:
          break
      except Exception as e:
        pass

class ElasticSearchTestServer(TestServer):
  def __init__(self, port = 9200):
    base_path = "/tmp/indexer_1/"
    filename = "elasticsearch-5.1.1" 
    zip_extension = ".tar.gz"
    url_base = "https://artifacts.elastic.co/downloads/elasticsearch/"
    hash_extension = ".sha1"
    cmd_start = [
      "bin/elasticsearch",
      "-Ehttp.port=" + str(port),
    ]
    cmd_clean = [
      "/bin/bash",
      "-c",
      "rm -rf ./data",
    ]
    super(ElasticSearchTestServer, self).__init__(base_path, filename, zip_extension, url_base, port, hash_extension, cmd_start, cmd_clean)

  def _test(self):
    for i in range(0, 10):
      time.sleep(2)
      try:
        resp = requests.get(self.get_url())
        resp.raise_for_status()
        break
      except Exception as e:
        pass

BUFFER = 1024

def download_file(filename, url_base, output_path, sha1 = None, md5 = None):
  # Download file
  data1 = url_base + filename
  r = requests.get(data1, stream=True)
  total = None
  if 'content-length' in r.headers:
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

