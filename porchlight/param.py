"""A constainer class for arbitrary data, with type and state checking.

|Param| is the primary class introduces in this file. |Empty| is a singleton
class denoting an "empty" parameter. The :py:class:`ParameterError` class is
also defined here.
"""
from typing import Any, Callable, Type, Union

import logging

logger = logging.getLogger(__name__)


class ParameterError(Exception):
    """Error for Param-specific exceptions."""

    pass


class Empty:
    """An empty class representing missing parameters values.

    At initialization, if an instance does not already exist it is created. No
    instance of Empty exists until it has been instantiated once.

    It is recommended that |Empty| be used over :py:obj:`None` to denote
    parameters that have not been initialized with any value, so that
    :py:obj:`None` can be treated unambiguously when using |porchlight|.
    """

    def __new__(cls):
        # Return the singleton instance if it exists already, otherwise become
        # the singleton instance.
        if not hasattr(cls, "_singleton_instance"):
            cls._singleton_instance = super(Empty, cls).__new__(cls)

        return cls._singleton_instance

    def __eq__(self, other):
        if other is self:
            return True

        else:
            return False

    def __neq__(self, other):
        return not (self == other)


class Param:
    """Container class for arbitrary Python data.

    Although mutable, editing |Param| objects directly is strongly discouraged
    unless absolutely necessary.

    |Param| uses `__slots__`, and no attributes other than those listed below
    may be assigned to |Param| objects.

    Attributes
    ----------
    _name : :py:obj:`str`
        Parameter name.

    _value : :py:class:`~typing.Any`
        Value of the parameter. If the parameter does not contain an assigned
        value, this should be |Empty|.

    _type : :py:class:`~typing.type`
        The type corresponding to the type of :py:attr:`Param._value`.

    constants : :py:obj:`bool`
        True if this object should be considered a constant. If the |Param|
        value is modified by :py:attr:`Param.value`'s `setter`, but
        `constant` is True, a :py:class:`~porchlight.param.ParameterError` will
        be raised.

    restrict : `Callable` or `None`
        If a callable, it will be invoked on the parameter whenever the
        parameter is changed. If it evaluates to False, a |ParameterError| is
        raised.

        Example: "temperature" parameter should not be negative or zero in our
        model:

        .. code-block::python

            temp = Param(
                "temperature",
                restrict=lambda x: x > 0
            )

            # The below would raise a ParameterError, the check occuring
            # automatically.
            temp.value = -500

        See :py:attr:`Param.value` for further details.
    """

    # A parameter, to be updated from the API, needs to be replaced rather than
    # reassigned. That said there are a few use cases where it may be useful to
    # have easy access, so just hiding these behind properties.
    __slots__ = ["_name", "_value", "constant", "_type", "restrict"]

    def __init__(
        self,
        name: str,
        value: Any = Empty(),
        constant: bool = False,
        restrict: Union[Callable, None] = None,
    ):
        """Initializes the Param object.

        Arguments
        ---------
        name : :py:obj:`str`
            Parameter name.

        value : :py:class:`~typing.Any`
            Value of the parameter. If the parameter does not contain an
            assigned value, this should be `~porchlight.param.Empty`

        constant : :py:obj:`bool`
            True if this object should be considered a constant. If the |Param|
            value is modified by `Param.value`'s `setter`, but `constant` is
            True, a :class:`~porchlight.param.ParameterError` will be raised.

        restrict : :py:class:`~typing.Callable` or `None`
            If a callable is passed, whenever the value property of the
            parameter is set, restrict will be called on the candidate value.
            If the result evaluates to False, a ParameterError will be raised.
        """
        self._name = name
        self._value = value
        self.constant = constant
        self._type = type(self._value)
        self.restrict = restrict

    def __repr__(self):
        info = {
            "name": self.name,
            "value": self.value,
            "constant": self.constant,
            "type": self.type,
        }

        infostrings = [f"{key}={repr(value)}" for key, value in info.items()]

        outstr = f"Param({', '.join(infostrings)})"

        return outstr

    def __eq__(self, other):
        if not isinstance(other, Param):
            return False

        for attr in self.__slots__:
            if getattr(self, attr) != getattr(other, attr):
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

        if self.restrict is not None:
            if not self.restrict(new_value):
                msg = f"Parameter restriction rejected value: {new_value}"
                logger.error(msg)
                raise ParameterError(msg)

        self._value = new_value

        # TODO: REFACTORING this should be typecheck upon request/by default in
        # a future update.
        self._type = type(self._value)

    @property
    def type(self) -> Type:
        return self._type
