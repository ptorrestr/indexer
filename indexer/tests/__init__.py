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

class TestServer(object):
  def __init__(self, base_path, filename, zip_extension, url_base, port, hash_extension):
    self.base_path = base_path
    self.filename = filename
    self.pidfile = base_path + filename + "server.pid"
    self.zip_extension = zip_extension
    self.url_base = url_base
    self.port = str(port)
    self.hash_extension = hash_extension

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
    pass

  def _test(self):
    pass

  def _stop(self):
    pass

  def _clean(self):
    pass

  def get_url(self):
    return "http://localhost:" + self.port

class NERTestServer(TestServer):
  def __init__(self, port = 8200):
    base_path = "/tmp/ner_1/"
    filename = "neel2016-nee-servlet-dda1ce83848c6c0dc6e3e436e0be4a2f183b5742"
    zip_extension = ".tar.gz"
    url_base = "http://srvgal80.deri.ie/~pabtor/"
    hash_extension = None
    super(NERTestServer, self).__init__(base_path, filename, zip_extension, url_base, port, hash_extension)

  def _start(self):
    cmd_start = [
      "/bin/bash",
      "-c",
      "mvn -Djetty.http.port=" + self.port + " jetty:run",
    ]
    self.proc = subprocess.Popen(cmd_start, cwd = self.base_path + self.filename)

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
    print("test done")

  def _stop(self):
    self.proc.kill()

class ElasticSearchTestServer(TestServer):
  def __init__(self, port = 9200):
    base_path = "/tmp/indexer_1/"
    filename = "elasticsearch-5.1.1" 
    zip_extension = ".tar.gz"
    url_base = "https://artifacts.elastic.co/downloads/elasticsearch/"
    hash_extension = ".sha1"
    super(ElasticSearchTestServer, self).__init__(base_path, filename, zip_extension, url_base, port, hash_extension)

  def _start(self):
    cmd_start = [
      self.base_path + self.filename + "/bin/elasticsearch",
      "--pidfile=" + self.pidfile,
      "-d",
      "-Ehttp.port=" + self.port,
    ]
    call(cmd_start, cwd = self.base_path)

  def _test(self):
    for i in range(0, 10):
      time.sleep(2)
      try:
        resp = requests.get(self.get_url())
        print(resp.status)
        resp.raise_for_status()
        break
      except Exception as e:
        pass

  def _stop(self):
    with open(self.pidfile) as f:
      pid = f.read()
    cmd_stop = [
      "/bin/bash",
      "-c",
      "kill -9 " + pid,
    ]
    call(cmd_stop, cwd = self.base_path)

  def _clean(self):
    cmd_clean = [
      "/bin/bash",
      "-c",
      "rm -rf " + self.base_path + self.filename + "/data",
    ]
    call(cmd_clean, cwd = self.base_path)

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

