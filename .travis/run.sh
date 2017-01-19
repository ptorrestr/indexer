set -e -x

source activate test-environment
python setup.py test
