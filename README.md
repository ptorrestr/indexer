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
* Stanford Ner Server:
 * In another folder, execute the following commands:
 * ``pip install git+https://bitbucket.org/torotoki/corenlp-python.git``
 * ``echo -e "annotators = tokenize, ssplit, pos, lemma, ner\n" > corenlp-python/corenlp/default.properties``
 * ``pip install pexpect``
 * ``pip install jsonrpclib-pelix``
 * ``pip install git+https://github.com/joshmarshall/jsonrpclib.git``
 * ``wget http://nlp.stanford.edu/software/stanford-corenlp-full-2014-08-27.zip``
 * ``unzip stanford-corenlp*.zip``
 * ``echo -e "from corenlp import corenlp\ncorenlp.main()" > server.py``
 * Run server: ``python server.py -S stanford-corenlp-full-2014-08-27/ -H 0.0.0.0 -p 3456``


Testing
-------
You must include the binary `rdf2hdt` from HDT project in the `PATH`. The tests assume that a stanford NER server is running in the localhost at port 3456.

Testing can be done by: ``python setup.py test``

Execution
---------
``dbpedia\_indexer`` requires the following parameters:
 * `` --url`` It is the URL of the Elastic Search server.
 * `` --name`` It is the index name where to store the data.
 * `` --file`` It is the dbpedia HDT file. 
 * `` --size`` The amount of lines read from the file per call.

Example:
``LOG_CFG='etc/logging.yaml' dbpedia_indexer --url http://localhost:9200 --name test --file test.dat.bz2 --size 10``

Delete Index
------------

``curl -X DELETE srvgal93:9200/test``
