# Initialize logging
import logging
import os

logging.basicConfig(filename=f"{os.getcwd()}/porchlight.log")
loggers = logging.getLogger(__name__)
