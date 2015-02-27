import os

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
    packages=['indexer', 'indexer.tests'],
    install_requires=[
      "pyaml >= 13.12.0",
      "requests >= 2.5.1",
      "t2db_objects >= 0.6.2",
      "hdtconnector >= 1.0",
      "pexpect >= 3.3",
      "jsonrpclib-pelix >= 0.2.4",
    ],
    entry_points = {
      'console_scripts':[
        'dbpedia_indexer = indexer.run:runIndexer',
      ]
    },
    test_suite='indexer.tests',
    zip_safe = False
)

