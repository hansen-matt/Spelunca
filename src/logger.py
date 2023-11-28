#!/usr/bin/python3

import logging as _logging

# Create a custom logger
logging = _logging.getLogger(__name__)
logging.setLevel(_logging.INFO)

log_handler = _logging.StreamHandler()
log_format = _logging.Formatter(
    "%(asctime)s - %(pathname)s:%(lineno)d - %(levelname)s - %(message)s"
)
log_handler.setFormatter(log_format)

logging.addHandler(log_handler)


DEBUG = _logging.DEBUG
INFO = _logging.INFO
WARNING = _logging.WARNING
ERROR = _logging.ERROR
FATAL = _logging.FATAL


if __name__ == "__main__":
    logging.setLevel(_logging.DEBUG)

    logging.debug("Watch out!")
    logging.info("Watch out!")
    logging.warning("Watch out!")
    logging.error("Watch out!")
    logging.fatal("Watch out!")
