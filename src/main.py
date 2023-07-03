import logging
import logging.config

import yaml

from application import Application
from exceptions import ApplicationStartUpError


def main():
    with open('logging.yaml', 'rt') as f:
        config = yaml.safe_load(f.read())
        f.close()

    logging.config.dictConfig(config)

    logger = logging.getLogger(__name__)
    try:
        Application.builder(config_dir='./config').build().run()
    except ApplicationStartUpError as ex:
        logger.error(f'Startup failed:\n{ex}')


if __name__ == '__main__':
    main()
