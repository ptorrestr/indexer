from multiprocessing import util
import subprocess
from setuptools import setup

def readme():
  with open('README.md') as f:
    return f.read()

def version():
  out = subprocess.Popen(['git','describe','--tags'], stdout = subprocess.PIPE, universal_newlines = True)
  out.wait()
  if out.returncode:
    with open('version') as f:
      return f.read()
  else:
    m_version = out.stdout.read().strip()
    print(m_version)
    with open('version', 'w') as f:
      f.write(m_version)
    return m_version

def dependencies():
  with open('dependencies') as f:
    return f.readlines()

setup(
  name='indexer',
  version = version(),
  description ='Indexer for dbpedia',
  long_description = readme(),
  classifiers = [
    'Programming Language :: Python :: 3.4',
  ],
  url = 'http://github.com/ptorrest/indexer',
  author = 'Pablo Torres',
  author_email = 'pablo.torres@insight-centre.org',
  license = 'GNU',
  packages = ['indexer', 'indexer.tests'],
  install_requires = dependencies(),
  entry_points = {
    'console_scripts':[
      'dbpedia_indexer = indexer.run:runIndexer',
    ]
  },
  test_suite = 'indexer.tests',
  zip_safe = False
)

