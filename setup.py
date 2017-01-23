from multiprocessing import util
import subprocess
from setuptools import setup

def readme():
  with open('README.md') as f:
    return f.read()

def version():
  out = subprocess.Popen(['git','describe','--tags'], stdout = subprocess.PIPE, universal_newlines = True)
  out.wait()
  if out.returncode == 0:
    m_version = out.stdout.read().strip()
    version = m_version.split("-")
    if len(version) > 0:
      print(version[0])
      return version[0]
  return "0.0.1" #default version

setup(
        name='indexer',
        version = version(),
        description ='Indexer for dbpedia',
        long_description = readme(),
        classifiers = [
            'Programming Language :: Python :: 3.5',
            ],
        url = 'http://github.com/ptorrest/indexer',
        author = 'Pablo Torres',
        author_email = 'pablo.torres.t@gmail.com',
        license = 'GNU',
        packages = ['indexer', 'indexer.tests'],
        entry_points = {
            'console_scripts':[
                'dbpedia_indexer = indexer.run:runIndexer',
                ]
            },
        test_suite = 'indexer.tests',
        zip_safe = False
        )

