#!/usr/bin/env bash

set -x -e

if [[ "$TRAVIS_OS_NAME" == "osx" ]]; then
  rvm get stable # We need this since there is a bug in osx. See https://github.com/travis-ci/travis-ci/issues/6307
  os="MacOSX"
else
  os="Linux"
  # Install docker
  sudo mkdir -p /etc/docker/certs.d/$DOCKER_URL 
  sudo wget $DOCKER_CERT_URL -O /etc/docker/certs.d/$DOCKER_URL/ca.crt
  sudo service docker restart
  # force vm size for elasticsearch
  # See https://www.elastic.co/guide/en/elasticsearch/reference/5.0/vm-max-map-count.html#vm-max-map-count
  sudo sysctl -w vm.max_map_count=262144
fi

if [[ "$TRAVIS_PYTHON_VERSION" == "2.7" ]]; then
  python_v="2"
else
  python_v="3"
fi
wget "https://repo.continuum.io/miniconda/Miniconda${python_v}-latest-${os}-x86_64.sh" -O miniconda.sh;
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
conda install conda-build anaconda-client
conda create -q -n indexer-test python=$TRAVIS_PYTHON_VERSION
