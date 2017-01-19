#!/usr/bin/env bash

set -x -e

if [[ "$TRAVIS_PYTHON_VERSION" == "2.7" ]]; then
  wget https://repo.continuum.io/miniconda/Miniconda2-latest-Linux-x86_64.sh -O miniconda.sh;
else
  wget https://repo.continuum.io/miniconda/Miniconda3-latest-Linux-x86_64.sh -O miniconda.sh;
fi
bash miniconda.sh -b -p $HOME/miniconda
export PATH="$HOME/miniconda/bin:$PATH"
hash -r
conda config --set always_yes yes --set changeps1 no
conda update -q conda
conda info -a

conda config --add channels salford_systems
conda config --add channels conda-forge
conda config --add channels ptorrestr
conda config --append channels pkgw
conda config --get channels
conda create -q -n test-environment python=$TRAVIS_PYTHON_VERSION
conda install -y -n test-environment \
  hdtconnector==0.2.1
source activate test-environment
python setup.py install
