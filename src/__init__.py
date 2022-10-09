# Initialize logging
import logging
import os

logging.basicConfig(filename=f"{os.cwd()}}/porchlight.log")
loggers = logging.getLogger(__name__)

