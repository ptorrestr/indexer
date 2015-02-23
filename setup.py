import os
from setuptools import setup
from setuptools.command.install import install
from distutils.command.build import build
from subprocess import call

BASEPATH = os.path.dirname(os.path.abspath(__file__))
STANFORD_PATH = os.path.join(BASEPATH, 'stanford')

class build_stanford(build):
  def run(self):
    # Run original build
    build.run(self)

    # Configure Stanford
    build_path = os.path.abspath(self.build_temp) 
    self.mkpath(build_path)
    stanford_version = '2014-08-27'
    stanford_prefix = 'stanford-corenlp-full'
    stanford_file_name = stanford_prefix + '-' + stanford_version + '.zip'
    stanford_file_path = build_path + '/' + stanford_file_name
    stanford_folder = build_path + '/' + stanford_prefix + '-' + stanford_version
    stanford_url_base = 'http://nlp.stanford.edu/software/'
    stanford_file_url = stanford_url_base + stanford_file_name
    print(stanford_file_url)
    cmd_curl = [
      '/bin/bash',
      '-c',
      'test -f ' + stanford_file_path + ' || curl ' + stanford_file_url + ' -o ' + stanford_file_path,
    ]

    cmd_unzip = [
      '/bin/bash',
      '-c',
      'unzip -o ' + stanford_file_path + ' -d ' + build_path  + ' && ' + 
      'cp -r ' + stanford_folder + ' ' + STANFORD_PATH + '/core',
    ]
    
    def stanford():
      print('*'*80)
      call(cmd_curl, cwd=BASEPATH)
      print('*'*80)
      call(cmd_unzip, cwd=BASEPATH)
      print('*'*80)

    self.execute(stanford, [], 'installing stanford NER')

    # copy to final destination
    self.copy_tree(STANFORD_PATH, self.build_lib + '/stanford')

class install_stanford(install):
  def initialize_options(self):
    install.initialize_options(self)
    self.build_scripts = None

  def finalize_options(self):
    install.finalize_options(self)
    self.set_undefined_options('build', ('build_scripts', 'build_scripts'))

  def run(self):
    # Run original install
    install.run(self)

    # Install Stanford NER
    print('installing stanford NER')
    self.copy_tree(self.build_lib, self.install_lib)
    

def readme():
    with open('README.md') as f:
        return f.read()

setup(
    name='indexer',
    version='0.0.1',
    description='Indexer for dbpedia',
    long_description = readme(),
    classifiers=[
      'Programming Language :: Python :: 3.4',
    ],
    url='http://github.com/ptorrest/indexer',
    author='Pablo Torres',
    author_email='pablo.torres@insight-centre.org',
    license='GNU',
    cmdclass = {
      'build' : build_stanford,
      'install' : install_stanford,
    },
    packages=['indexer', 'indexer.tests'],
    install_requires=[
      "pyaml >= 13.12.0",
      "requests >= 2.5.1",
      "t2db_objects >= 0.6.2",
      "hdtconnector >= 1.0",
      "unidecode >= 0.04.17",
      "pexpect >= 3.3",
    ],
    entry_points = {
      'console_scripts':[
        'dbpedia_indexer = indexer.run:runIndexer',
      ]
    },
    test_suite='indexer.tests',
    zip_safe = False
)

