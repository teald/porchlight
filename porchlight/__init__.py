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
import os

from .door import Door
from .neighborhood import Neighborhood
from .param import Param


# Initialize logging
import logging

logging.getLogger(__name__).addHandler(logging.NullHandler())
