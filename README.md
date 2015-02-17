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
dbpedia\_indexer --url ELASTIC\_SEARCH\_URL
                 --name ELASTIC\_SEARCH\_INDEX\_NAME
                 --file DBPEDIA\_BZ2\_FILE
                 --size BUFFER\_SIZE

Example:
``LOG\_CFG='etc/logging.yaml' dbpedia\_indexer --url http://localhost:9200 --name test --file test.dat.bz2 --size 10``

