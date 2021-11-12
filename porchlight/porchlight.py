'''Primary file for using porchlight. This handles imports, unit testing, etc.'''
# General imports
import pdb
import logging
import datetime
import os

# porchlight imports
import door

# Set up logging
if os.path.isfile('pl.log'):
    # Clear any previous logs.
    os.remove('pl.log')

logging.basicConfig(filename='pl.log', level=logging.DEBUG)

# Make sure the logger title name is descriptive in the case that a unit test
# is run (this file is outright executed.
if __name__ != "__main__":
    logger = logging.getLogger(__name__)

else:
    logger = logging.getLogger("porchlight")

logger.info(f"Began logger at {datetime.datetime.now()}")

if __name__ == "__main__":
    # Unit testing

    # door module
    door.__unit_test()

logger.info(f"Concluded logger at {datetime.datetime.now()}.")
