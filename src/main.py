import logging
import logging.config
import os.path
import sys

import yaml

from application import Application
from exceptions import ApplicationStartUpError


def load_logging_config():
    log_file_name = 'logging.yaml'
    default_logging_config = '''version: 1

formatters:
  simple:
    format: '%(asctime)s %(levelname)s %(thread)10d --- [%(threadName)15s] %(name)-30s : %(message)s'

handlers:
  console:
    class: logging.StreamHandler
    level: DEBUG
    formatter: simple

loggers:
  root:
    level: DEBUG
    handlers: [ console ]
'''
    if not os.path.exists(log_file_name):
        with open(log_file_name, 'w') as fp:
            fp.write(default_logging_config)
        config = yaml.safe_load(default_logging_config)
    else:
        if not os.path.isfile(log_file_name):
            print(f'Logging config {log_file_name} is not a file')
            sys.exit(-1)
        if not os.access(log_file_name, os.R_OK):
            print(f'Logging config {log_file_name} is not readable')
            sys.exit(-1)
        with open(log_file_name, 'r') as fp:
            config = yaml.safe_load(fp.read())

    logging.config.dictConfig(config)


def main():
    load_logging_config()

    logger = logging.getLogger(__name__)
    try:
        Application.builder(config_dir='./config').build().run()
    except ApplicationStartUpError as ex:
        logger.error(f'Startup failed:\n{ex}')


if __name__ == '__main__':
    main()
