"""`porchlight` is a library meant to reduce the complexity and stress of
coupling models or providing a very simple python API.

.. include:: substitutions.rst

It contains three classes especially imported by this file to the main
package-level namespace:
+   |Neighborhood|
+   |Door|
+   |Param|

Please see their respective documentation for details on usage, or check out
the |porchlight| :doc:`quickstart` guide

"""
import logging
import os

from .door import Door
from .neighborhood import Neighborhood
from .param import Param


# Aliases for migration to generic names, >=v1.2.0.
PorchlightAdapter = Door
PorchlightMediator = Neighborhood
PorchlightContainer = Param


# Initialize logging with a NullHandler to let user decide on a handler if they
# so choose.
logging.getLogger(__name__).addHandler(logging.NullHandler())
