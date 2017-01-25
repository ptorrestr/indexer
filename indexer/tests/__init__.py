import logging

from t2db_objects.logger import setup_logging

setup_logging('etc/logging_debug.yaml')
logger = logging.getLogger(__name__)

