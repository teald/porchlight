from typing import Any


class Param:
    __slots__ = [
            "_name",
            "_value",
            "constant"
            ]

    def __init__(self, name: str, value: Any, constant: bool = False):
        '''Initializes the Param object.'''
        self._name = name
        self._value = value
        self.constant = constant

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
