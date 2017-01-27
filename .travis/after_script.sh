#!/usr/bin/env bash

set -x -e

containers=$(cat .containers)
for container_id in $containers; do
  docker stop $container_id
  docker rm $container_id
done
rm .containers
