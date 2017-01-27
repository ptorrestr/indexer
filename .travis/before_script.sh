#!/usr/bin/env bash

set -x -e

docker login $DOCKER_URL -u $DOCKER_USER -p $DOCKER_PASSWORD
docker run -d -p 8080:8080 $DOCKER_URL/ner
