#!/usr/bin/env bash

set -x -e

export PATH="$HOME/miniconda/bin:$PATH"
source activate indexer-test
file=$(conda build .conda/ --output)
anaconda -t $ANACONDA_TOKEN upload $file -u $ANACONDA_USER --force
