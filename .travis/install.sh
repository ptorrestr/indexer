#!/usr/bin/env bash

set -x -e

export PATH="$HOME/miniconda/bin:$PATH"
source activate indexer-test
conda build .conda/ --no-test --no-anaconda-upload
