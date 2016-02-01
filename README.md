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
 * `` --ner-url`` A NER REST service endpoint.
 * `` --num-threads`` Number of threads that will read the hdt file.
 * `` --index-config`` Configuration file in json format for ElasticSearch

Example:
``LOG_CFG='etc/logging.yaml' dbpedia_indexer --url http://my-es --name test --file ~/myfile.hdt --size 1000 --ner-url http://my-server/nee --num-threads 8 --index-config my_config.json``

Delete Index
------------

``curl -X DELETE srvgal93:9200/test``
