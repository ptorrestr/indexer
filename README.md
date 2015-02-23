Indexer
=======

Installation
------------

Dependencies:
* pyaml
* requests
* t2db\_objects (``pip install git+https://gitlab.insight-centre.org/hujo/t2db_objects.git``)
* hdtconnector:
 * You must have installed HDT and Boost (See https://github.com/ptorrestr/hdt-connector)
 * Clone the project: `git clone https://github.com/ptorrestr/hdt-connector`
 * Update the ENV variables in file setup.py
 * Install normally (`python setup.py install`)
* Stanford Ner:
 * ``pip install git+https://bitbucket.org/torotoki/corenlp-python.git``
 * Download Standford `wget http://nlp.stanford.edu/software/stanford-corenlp-full-2014-08-27.zip`
 * `unzip stanford-corenlp-full-2014-08-27.zip`


Execution
---------
``dbpedia\_indexer`` requires the following parameters:
 * `` --url`` It is the URL of the Elastic Search server.
 * `` --name`` It is the index name where to store the data.
 * `` --file`` It is the dbpedia bz2 file. 
 * `` --size`` The amount of lines read from the file per call.

Example:
``LOG_CFG='etc/logging.yaml' dbpedia_indexer --url http://localhost:9200 --name test --file test.dat.bz2 --size 10``

