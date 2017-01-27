#!/usr/bin/env bash

set -x -e

DOCKER_URL=${DOCKER_URL:-`hostname -f`}
cat ~/.docker/config.json | grep $DOCKER_URL \
	|| docker login $DOCKER_URL -u $DOCKER_USER -p $DOCKER_PASSWORD
echo "export NER_URL=\"http://$(hostname):8080/ner\"" > .env
echo "export ELASTICSEARCH_URL=\"http://$(hostname):9200\"" >> .env
docker run -d -p 9200:9200 \
	docker.elastic.co/elasticsearch/elasticsearch:5.1.1 >> .containers
docker run -d -p 8080:8080 \
	$DOCKER_URL/ner >> .containers