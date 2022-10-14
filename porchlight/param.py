from typing import Any, Type

import logging
logger = logging.getLogger(__name__)


class ParameterError(Exception):
    '''Errors due to Param-specific issues.'''
    pass


class Empty:
    '''An empty class representing missing parameters values. Repurposed here
    from the inspect module.
    '''
    def __init__(self):
        pass

    def __eq__(self, other):
        '''Force Equality of this special value regardless of whether it is
        initialized or not
        '''
        if isinstance(other, Empty) or other == Empty:
            return True

        else:
            return False


class Param:
    '''Parameter class. while not frozen, for most purposes it should not be
    modified outside of a porchlight object.
    '''
    # A parameter, to be updated from the API, needs to be replaced rather than
    # reassigned. That said there are a few use cases where it may be useful to
    # have easy access, so just hiding these behind properties.
    __slots__ = [
            "_name",
            "_value",
            "constant",
            "_type"
            ]

    def __init__(self, name: str,
                 value: Any = Empty(),
                 constant: bool = False
                 ):
        '''Initializes the Param object.'''
        self._name = name
        self._value = value
        self.constant = constant
        self._type = type(self._value)

    def __str__(self):
        outstr = f"{self._name} ({self._type}): {self._value}"
        outstr += "" if not self.constant else " (constant)"
        return outstr

    def __eq__(self, other):
        if not isinstance(other, Param):
            return False

        for attr in self.__slots__:
            if (getattr(self, attr) != getattr(other, attr)):
                return False

        return True

    @property
    def name(self):
        return self._name

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, new_value: Any):
        if self.constant:
            msg = f"Parameter {self.name} is not mutable."
            logger.error(msg)
            raise ParameterError(msg)

        self._value = new_value

        # TK REFACTORING this should be typecheck upon request/by default in a
        # future update.
        self._type = type(self._value)

    @property
    def type(self) -> Type:
        return self._type
