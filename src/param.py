from typing import Any, Dict, Type


class ParameterError(Exception):
    '''Errors due to Param-specific issues.'''
    pass

class Empty:
    '''An empty class representing missing parameters values. Repurposed here
    from the inspect module.
    '''
    def __init__(self):
        pass

empty = Empty()

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
            "_type",
            "__empty"
            ]

    def __init__(self, name: str, value: Any = empty, constant: bool = False):
        '''Initializes the Param object.'''
        self._name = name
        self._value = value
        self.constant = constant
        self._type = type(self._value)

    @property
    def name(self):
        return self._name

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, new_value: Any):
        if self.constant:
            raise ValueError(f"Param object {self.__name__} is not mutable.")

        self._value = new_value

    @property
    def type(self) -> Type:
        return self._type
