import inspect
import string

from .param import Empty, ParameterError, Param

from typing import Any, Callable, Dict, List, Type

import logging

logger = logging.getLogger(__name__)


class BaseDoor:
    """Contains the basic information of a Door object, as well as base
    functions.

    Attributes
    ----------
    arguments : :py:obj:`dict`, :py:obj:`str`: :class:`~typing.Type`
        Dictionary of all arguments taken as input when the `BaseDoor` object
        is called.

    keyword_args : :py:obj:`dict`, :py:obj:`str`: :class:`~typing.Any`
        Keyword arguments accepted by the `BaseDoor` as input when called. This
        includes all arguments that are not positional-only. Positional
        arguments without a default value are assigned a
        :class:~porchlight.param.Empty` value instead of their default value.

    max_n_return : :py:obj:`int`
        Maximum number of returned values.

    min_n_return : :py:obj:`int`
        Minimum number of returned values.

    n_args : :py:obj:`int`
        Number of arguments accepted by this `BaseDoor`

    name : :py:obj:`str`
        The name of the function as visible from the base function's __name__.

    return_vals : :py:obj:`list` of :py:obj:`list` of :py:obj:`str`
        Values returned by any return statements in the base function.

    typecheck : :py:obj:`bool`
        If True, when arguments are passed to the `BaseDoor`'s base function
        the input types are checked against the types in `BaseDoor.arguments`.
        If there is a mismatch, a `TypeError` will be thrown.

    _base_function : :py:obj:`~typing.Callable`
        This holds a reference to the function being managed by the `BaseDoor`
        instance.
    """

    _base_function: Callable
    arguments: Dict[str, Type]
    keyword_args: Dict[str, Any]
    max_n_return: int
    min_n_return: int
    n_args: int
    name: str
    return_vals: List[List[str]]
    typecheck: bool

    def __init__(self, function: Callable, typecheck: bool = True):
        """Initializes the BaseDoor class. It takes any callable (function,
        lambda, method...) and inspects it to get at its arguments and
        structure.

        if typecheck is True (default True), the type of inputs passed to
        BaseDoor.__call__ will be checked for matches to known input Types.

        Parameters
        ----------
        function : :py:class:`typing.Callable`
            The callable/function to be managed by the BaseDoor class.

        typecheck : :py:obj:`bool`, optional
            If `True`, the `BaseDoor` object will assert that arguments passed
            to `__call__` (when the `BaseDoor` itself is called like a
            function) have the type expected by type annotations and any user
            specifications. By default, this is `True`.
        """
        self._base_function = function
        self.typecheck = typecheck
        self._inspect_base_callable()

    def __eq__(self, other) -> bool:
        """Equality is defined as referencing the same base function."""
        if self.name is other.name:
            return True

        return False

    def _inspect_base_callable(self):
        """Inspect the BaseDoor's baseline callable for primary attributes.

        This checks for type annotations, return statements, and all
        information accessible to :py:obj:`inspect.Signature` relevant to
        `BaseDoor`.
        """
        function = self._base_function

        self.name = function.__name__
        self.__name__ = function.__name__
        self.arguments = {}
        self.keyword_args = {}
        self.keyword_only_args = {}

        for name, param in inspect.signature(function).parameters.items():
            self.arguments[name] = param.annotation

            # Check for positional-only arguments first, then proceed to other
            # argument types.
            if param.kind == inspect.Parameter.POSITIONAL_ONLY:
                msg = (
                    f"porchlight does not support positional-only "
                    f"arguments, which were found in {self.name}."
                )

                logger.error(msg)
                raise NotImplementedError(msg)

            elif param.default != inspect._empty:
                self.keyword_args[name] = Param(name, param.default)

                if param.kind == inspect.Parameter.KEYWORD_ONLY:
                    self.keyword_only_args[name] = Param(name, param.default)

            elif param.kind == inspect.Parameter.KEYWORD_ONLY:
                # This catches keyword-only arguments with no default value.
                # ^ TKREFACTORING is that a thing we need to worry about?
                self.keyword_args[name] = Param(name, Empty())
                self.keyword_only_args[name] = Param(name, Empty())

            else:
                self.keyword_args[name] = Param(name, Empty())

        for name, _type in self.arguments.items():
            if _type == inspect._empty:
                self.arguments[name] = Empty

        self.n_args = len(self.arguments)

        # The return values require some more effort.
        self.return_vals = self._get_return_vals(function)

        logger.debug(f"Found {self.n_args} arguments in {self.name}.")

    def __call__(self, *args, **kwargs):
        """Calls the BaseDoor's function as normal.

        The keys of kwargs must be passed with the same name as variables
        within the BaseDoor. As of right now, if extra values are included,
        they are ignored.
        """
        # This is currently filtering out all the arguments the function
        # actually needs. But this way of doing it should probably be handled
        # by the Neighborhood object in the future.
        # ^ TK REFACTORING
        input_kwargs = {k: v for k, v in kwargs.items() if k in self.arguments}

        # Type checking.
        if self.typecheck:
            for k, v in input_kwargs.items():
                if self.arguments[k] == Empty:
                    continue

                if not isinstance(v, self.arguments[k]):
                    msg = (
                        f"Type checking is on, and the type for input "
                        f"parameter {k}, {type(v)} to {self.name} does not "
                        f"match the detected type(s), {self.arguments}"
                    )

                    logger.error(msg)
                    raise ParameterError(msg)

        return self._base_function(*args, **input_kwargs)

    @staticmethod
    def _get_return_vals(function: Callable) -> List[str]:
        """Gets the names of the return value variables for a given
        function.
        """
        lines, start_line = inspect.getsourcelines(function)

        # These characters signal that the return statement does not contain
        # any operations on the return values, which is undefined for the
        # purposes of the BaseDoor
        allowed_chars = list(string.ascii_letters + string.digits + "_")

        return_vals = []
        ret_statement = "return "
        ret_statement_len = len(ret_statement)

        for i, line in enumerate(lines):
            orig_line = line

            # Strip comments.
            if "#" in line:
                line = line[: line.index("#")]

            if "return " == line.strip()[:ret_statement_len]:
                # This is a set of possible return values.
                line = line.strip()[ret_statement_len:]
                vals = line.split(",") if "," in line else [line]
                vals = [v.strip() for v in vals]

                for val in vals:
                    if any(c not in allowed_chars for c in val):
                        # This is undefined, not an error. So assign return
                        # value 'undefined' for this return statement and issue
                        # a warning.
                        source_file = inspect.getfile(function)
                        logger.warning(
                            f"Could not define any set of return variable "
                            f"names for the following return line: \n"
                            f"{source_file}: {start_line+i}) "
                            f"{orig_line.strip()}\n While not crucial to "
                            f"this function, be aware that this means no "
                            f"return value will be modified by this "
                            f"callable."
                        )

                        vals = [None]
                        break

                return_vals.append(vals)

        return return_vals


class Door(BaseDoor):
    """Inherits from and extends :class:`~porchlight.door.BaseDoor`"""

    def __init__(self, function: Callable):
        super().__init__(function)

    @property
    def variables(self) -> List[str]:
        """Returns a list of all known return values and input arguments."""
        all_vars = []

        for arg in self.arguments:
            if arg not in all_vars:
                all_vars.append(arg)

        for ret in self.return_vals:
            for r in ret:
                if r not in all_vars:
                    all_vars.append(r)

        return all_vars

    @property
    def required_arguments(self) -> List[str]:
        """Returns a list of arguments with no default values."""
        required = []

        for x in self.arguments:
            if isinstance(self.keyword_args[x].value, Empty):
                required.append(x)

        return required
