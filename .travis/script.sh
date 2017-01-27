#!/usr/bin/env bash

set -e -x

export PATH="$HOME/miniconda/bin:$PATH"
source activate indexer-test
source .env
conda build -t .conda/
