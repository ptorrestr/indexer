#!/usr/bin/env bash

set -x -e

# Only publish when master is build
if [[ "$TRAVIS_BRANCH" == "master" ]]; then
  export PATH="$HOME/miniconda/bin:$PATH"
  source activate indexer-test
  file=$(conda build .conda/ --output)
  anaconda -t $ANACONDA_TOKEN upload $file -u $ANACONDA_USER --force
fi
