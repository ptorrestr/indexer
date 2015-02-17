Indexer
=======

Installation
------------

Dependencies:
* pyaml
* requests
* t2db\_objects (``pip install git+https://gitlab.insight-centre.org/hujo/t2db_objects.git``)


Execution
---------
``dbpedia\_indexer`` requires the following parameters:
 * `` --url`` It is the URL of the Elastic Search server.
 * `` --name`` It is the index name where to store the data.
 * `` --file`` It is the dbpedia bz2 file. 
 * `` --size`` The amount of lines read from the file per call.

Example:
``LOG_CFG='etc/logging.yaml' dbpedia_indexer --url http://localhost:9200 --name test --file test.dat.bz2 --size 10``

