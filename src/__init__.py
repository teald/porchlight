# Initialize logging
import logging
import os

logging.basicConfig(filename=f"{os.getcwd()}/porchlight.log")
loggers = logging.getLogger(__name__)

# Allow Neighborhood and Door to be directly importable.
from neighborhood import Neighborhood
from door import Door
