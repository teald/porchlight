# Initialize logging
import logging
import os

from .door import Door
from .neighborhood import Neighborhood
from .param import Param

logging.basicConfig(filename=f"{os.getcwd()}/porchlight.log")
loggers = logging.getLogger(__name__)
