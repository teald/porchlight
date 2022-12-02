import functools
import inspect
import itertools
import re
import types

from .param import Empty, ParameterError, Param
from .utils.typing_functions import decompose_type
from .utils.inspect_functions import get_all_source, get_wrapped_function

import copy
import typing
from typing import Any, Callable, Dict, List, Type

import logging

logger = logging.getLogger(__name__)


class DoorError(Exception):
    pass


class BaseDoor:
    """Contains the basic information of a Door object, as well as base
    functions.

    Attributes
    ----------
    arguments : :py:obj:`dict`, :py:obj:`str`: :class:`~typing.Type`
        Dictionary of all arguments taken as input when the `BaseDoor` object
        is called.

    positional_only : :py:obj:`list` of :py:obj:`str`
        List of positional-only arguments accepted by the function.

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

    return_types : :py:obj:`list` of :py:obj:`list` of `~typing.Type`
        Values returned by any return statements in the base function.

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
    return_types: List[List[Type]]
    return_vals: List[List[str]]
    typecheck: bool

    def __init__(
        self,
        function: Callable,
        typecheck: bool = True,
        returned_def_to_door: bool = False,
    ):
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

        returned_def_to_door : :py:obj:`bool`, optional
            Returns a Door generated from the output of the base function.
            Note, this is not the same as a DynamicDoor, and internal
            variables/updating is not handled as with a DynamicDoor. This just
            calls Door's initializer on the output of the base function.
        """
        self._returned_def_to_door = returned_def_to_door
        self._base_function = function
        self.typecheck = typecheck
        self._inspect_base_callable()

    def __eq__(self, other) -> bool:
        """Equality is defined as referencing the same base function."""
        if isinstance(other, BaseDoor) and self.name is other.name:
            return True

        return False

    def __repr__(self):
        info = {
            "name": self.name,
            "base_function": self._base_function,
            "arguments": self.arguments,
            "return_vals": self.return_vals,
        }

        substrs = [f"{key}={value}" for key, value in info.items()]

        outstr = f"BaseDoor({', '.join(substrs)})"

        return outstr

    def _inspect_base_callable(self):
        """Inspect the BaseDoor's baseline callable for primary attributes.

        This checks for type annotations, return statements, and all
        information accessible to :py:obj:`inspect.Signature` relevant to
        `BaseDoor`.
        """
        # Need to find the un-wrapped function that actually takes the
        # arguments in the end.
        function = get_wrapped_function(self._base_function)

        self.name = function.__name__
        self.__name__ = function.__name__
        self.arguments = {}
        self.positional_only = []
        self.keyword_args = {}
        self.keyword_only_args = {}

        try:
            ret_type_annotation = typing.get_type_hints(function)["return"]
            self.return_types = decompose_type(
                ret_type_annotation, include_base_types=False
            )

        except KeyError as e:
            # No return types there.
            logger.info(f"No return type hints found for {self.name}.")
            logger.debug(
                f"KeyError message for missing return type hints: {str(e)}"
            )

            self.return_types = None

        except TypeError as e:
            # This may be a real function that just doesn't have return types.
            logger.info(
                f"Function proceeding without return types due to "
                f"a TypeError raised while attempting to inspect the "
                f"source: {e}"
            )

            if isinstance(function, Callable):
                # This is still a function, and has otherwise worked.
                pass

        # Ensure the function can be inspected. If not, raise
        # NotImplementedError
        if not self._can_inspect(function):
            msg = (
                f"Function {self.name} could not be inspected and is not "
                f"yet supported. You should wrap the function within a "
                f"user-defined function, something like:\n\n"
                f"    def new_func(arg1, arg2, ..., kwarg1, kwarg2, ... ): \n"
                f"        output1, output2, ... = YOUR_FUNC(...)\n"
                f"        return output1, output2, ...\n\n"
            )

            logger.error(msg)
            raise NotImplementedError(msg)

        # Use function signature to introspect properties about the parameters.
        for name, param in inspect.signature(function).parameters.items():
            self.arguments[name] = param.annotation

            # Check for positional-only arguments first, then proceed to other
            # argument types.
            if param.kind == inspect.Parameter.POSITIONAL_ONLY:
                # Positional-only arguments will not support default values for
                # the function. That said, this is effectively overriden by
                # Neighborhood objects, since they store the parameter's value
                # and pass it regardless of whether the argument is
                # positional-only or not.
                self.positional_only.append(name)

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

    @property
    def __closure__(self):
        """Since BaseDoor is a wrapper, and we use utils.get_all_source to
        retrieve source, I'm mimicking the type a function wrapper would have
        here.
        """
        return (types.CellType(self._base_function),)

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

        return_val = self._base_function(*args, **input_kwargs)

        if self._returned_def_to_door:
            if not isinstance(return_val, BaseDoor):
                return_val = BaseDoor(return_val)

        return return_val

    @staticmethod
    def _can_inspect(f: Callable) -> bool:
        """Returns True if f can be used with :py:func:`inspect.signature`."""
        try:
            inspect.signature(f)

        except ValueError as e:
            logger.info(
                f"Function {f.__name__} is not inspectable! "
                f"{type(e).__name__}: {e}."
            )

            return False

        return True

    @staticmethod
    def _get_return_vals(function: Callable) -> List[str]:
        """Gets the names of the return value variables for a given
        function.

        For functions that wrap other functions (i.e., the return value is a
        function def'd in the function body), the return statements in the body
        are not parsed.

        Arguments
        ---------
        function : :py:class:`typing.Callable`
            The function to retrieve the return values for.
        """
        return_vals = []

        lines, start_line = get_all_source(function)

        # Tracking indentation for python-like parsing.
        cur_indent = 0
        last_check_indent = 0
        checking_for_returns = True
        main_def_found = False

        # These include mandatory space at the beginning since syntactically
        # there must exist non-\n whitespace for all lines after a funciton
        # definition.
        defmatch_str = r"^(\ )+def\s+"
        retmatch_str = r".*\s+return\s(.*)"
        indentmatch_str = r"^(\s)*"

        for i, line in enumerate(lines):
            orig_line = line.strip()

            # Remove comments
            if "#" in line:
                line = line[: line.index("#")]

            # Ignore empty lines
            if not line.strip():
                continue

            # Get the current indent level.
            indentmatch = re.match(indentmatch_str, line)
            cur_indent = len(indentmatch.group())

            # Ignore empty lines
            # Check for matches for both, in case there's something like
            #   def wtf(): return 5
            # Which is atrocious but possible.
            defmatch = re.match(defmatch_str, line)
            retmatch = re.match(retmatch_str, line)

            # Ignore decorators
            if re.match(r"\s*@\w+.*", line):
                continue

            # Catch in-function definitions and ignore them.
            if defmatch and i > 0 and main_def_found:
                checking_for_returns = False
                last_check_indent = cur_indent
                continue

            if not main_def_found and defmatch:
                main_def_found = True

            if not checking_for_returns and cur_indent <= last_check_indent:
                # This is outside the def scope
                checking_for_returns = True
                last_check_indent = 0

            if not checking_for_returns:
                continue

            if retmatch:
                # This is a return value that belongs to the object.
                ret_string = retmatch.group(1)
                if "," in ret_string:
                    vals = ret_string.split(",")

                else:
                    vals = [ret_string]

                vals = [v.strip() for v in vals]

                for val in vals:
                    if not re.match(r"\w+$", val):
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

                        vals = []
                        break

                if vals:
                    return_vals.append(vals)

        return return_vals

    @property
    def keyword_arguments(self):
        return self.keyword_args

    @property
    def kwargs(self):
        return self.keyword_args


class Door(BaseDoor):
    """Inherits from and extends :class:`~porchlight.door.BaseDoor`"""

    def __init__(
        self, function: Callable = None, *, argument_mapping: dict = {}
    ):
        self.argmap = argument_mapping

        self.function_initialized = False
        if function is None:
            return

        self.__call__(function)

    def __call__(self, *args, **kwargs):
        if not self.function_initialized:
            # Need to recieve the function.
            if len(args) != 1:
                msg = f"Expected a function, but recieved {args}"

                if kwargs:
                    msg += f" and kwargs {kwargs}. Has Door been initialized?"

                logger.error(msg)
                raise ValueError(msg)

            if not isinstance(args[0], Callable):
                msg = f"Cannot initialize this object as a door: {args[0]}"
                logger.error(msg)
                raise TypeError(msg)

            function = args[0]
            super().__init__(function)
            self.function_initialized = True

            # Perform any necessary argument mapping.
            self.map_arguments()

            return self

        # Check argument mappings.
        if not self.argmap:
            # Just pass arguments normally
            return super().__call__(*args, **kwargs)

        input_kwargs = {}
        for key, value in kwargs.items():
            if key in self.argmap:
                input_kwargs[self.argmap[key]] = value

            else:
                input_kwargs[key] = value

        # Temporarily restore the original arguments for the purposes of
        # 'BaseDoor.__call__'.
        _temp_arguments = self.arguments
        _temp_keyword_arguments = self.keyword_args
        self.arguments = self.original_arguments
        self.keyword_args = self.original_kw_arguments

        result = super().__call__(*args, **input_kwargs)

        self.arguments = _temp_arguments
        self.keyword_args = _temp_keyword_arguments

        return result

    def map_arguments(self):
        """Maps arguments if self.argmap is not {}."""
        if not self.function_initialized:
            msg = "Door has not yet been initialized with a function."
            logging.error(msg)
            raise DoorError(msg)

        if self.argmap:
            Door._check_argmap(self.argmap)

            arg_order = tuple(self.arguments.keys())
            kwarg_order = tuple(self.kwargs.keys())

            for mapped_name, old_name in self.argmap.items():
                # Catch mappings that would conflict with an existing key.
                if mapped_name in self.arguments:
                    msg = (
                        f"Conflicting map key: {mapped_name} is in arguments "
                        f"list."
                    )

                    logger.error(msg)
                    raise DoorError(msg)

                if old_name not in self.arguments:
                    msg = f"{old_name} is not a valid argument for {self.name}"
                    logger.error(msg)
                    raise DoorError(msg)

                self.arguments[mapped_name] = self.arguments[old_name]
                del self.arguments[old_name]

                # Change keyword arguments as well.
                if old_name in self.keyword_args:
                    self.keyword_args[mapped_name] = self.keyword_args[
                        old_name
                    ]

                    # Need to change the parameter name to reflect the mapping.
                    self.keyword_args[mapped_name]._name = mapped_name

                    del self.keyword_args[old_name]

                # Also change outputs that contain the same name.
                for i, ret_tuple in enumerate(self.return_vals):
                    for j, ret_val in enumerate(ret_tuple):
                        if old_name == ret_val:
                            self.return_vals[i][j] = mapped_name

            # Place back in the original order.
            rev_argmap = {v: k for k, v in self.argmap.items()}

            arg_order = (
                k if k not in rev_argmap else rev_argmap[k] for k in arg_order
            )

            kwarg_order = (
                k if k not in rev_argmap else rev_argmap[k]
                for k in kwarg_order
            )

            self.arguments = {a: self.arguments[a] for a in arg_order}
            self.keyword_args = {a: self.keyword_args[a] for a in kwarg_order}

    def _check_argmap(argmap):
        """Assesses if an argument mapping is valid, raises an appropriate
        exception if it is invalid. Will also raise warnings for certain
        non-fatal actions.
        """
        for key, value in argmap.items():
            # Argument map should contain valid python variable names.
            if not re.match(r"^[a-zA-Z_]([a-zA-Z0-9_])*$", key):
                msg = f"Not a valid map name: {key}"
                logging.error(msg)
                raise DoorError(msg)

    def __repr__(self):
        return super().__repr__().replace("BaseDoor", "Door")

    @property
    def original_arguments(self):
        arguments = copy.copy(self.arguments)

        for i, arg in enumerate(self.arguments):
            if arg in self.argmap:
                orig_arg = self.argmap[arg]
                _type = arguments[arg]

                arguments[orig_arg] = _type
                del arguments[arg]

        return arguments

    @property
    def original_kw_arguments(self):
        arguments = copy.copy(self.keyword_args)

        for i, arg in enumerate(self.keyword_args):
            if arg in self.argmap:
                orig_arg = self.argmap[arg]
                _type = arguments[arg]

                arguments[orig_arg] = _type
                del arguments[arg]

        return arguments

    @property
    def original_return_vals(self):
        return_vals = copy.copy(self.return_vals)

        # Also change outputs that contain the same name.
        for i, ret_tuple in enumerate(self.return_vals):
            for j, ret_val in enumerate(ret_tuple):
                if ret_val in self.argmap:
                    return_vals[i][j] = self.argmap[ret_val]

        return return_vals

    @property
    def argument_mapping(self):
        return self.argmap

    @argument_mapping.setter
    def argument_mapping(self, value):
        self.arguments = self.original_arguments
        self.keyword_args = self.original_kw_arguments
        self.argmap = value
        self.map_arguments()

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


class DynamicDoor(Door):
    """A dynamic door takes a door-generating function as its initializer.

    Unlike `~porchlight.door.BaseDoor`s and `~porchlight.door.Door`s, dynamic
    doors will only parse the definition's source once it is generated.

    These objects a function that returns a Door. The `DynamicDoor` then
    contains identical attributes to the generated door. Once called again, all
    attributes update to match the most recent call.

    Attributes
    ----------
    _door_generator : `Callable`
        A function returning a `~porchlight.door.Door` as its output.

    generator_args : `List`
        List of arguments to be passed as positional arguments to the
        `_door_generator` function.

    generator_kwards : `Dict`
        Dict of key: value pairs representing keyword arguments to be passed as
        positional arguments to the `_door_generator` function.
    """

    def __init__(
        self,
        door_generator: Callable[Any, Door],
        generator_args: List = [],
        generator_kwargs: Dict = {},
    ):
        """Initializes the Dynamic Door. When __call__ is invoked, the door
        generator is called.

        Arguments
        ---------
        _door_generator : `~typing.Callable[Any, Door]`
            A callable function that returns an initialized Door object.

        generator_args : `~typing.List`
            List of positional arguments for the generator function.

        generator_kwargs : `~typing.Dict[str, Any]`
            Dictionary of `str`/`Any` key/value pairs for keyword arguments
            passed to the generator function.
        """
        self._door_generator = door_generator
        self.generator_args = generator_args
        self.generator_kwargs = generator_kwargs

        # In order to pass some checks, a few key attributes need to be
        # initialized. These will be initialized to whatever value evaluates to
        # False for the relevant type.
        self.name = ""
        self.__name__ = ""
        self.arguments = {}
        self.keyword_args = {}
        self.keyword_only_args = {}
        self.return_vals = []
        self._cur_door = None
        self._last_door = None

    def __call__(self, *args, **kwargs) -> Any:
        """Executes the function stored in
        `~porchlight.door.DynamicDoorc._base_function` once
        `~porchlight.door.DynamicDoor.update` has executed.

        Arguments
        ---------
        *args : positional arguments
            Arguments directly passed to
            `~porchlight.door.DynamicDoor._base_function`.

        **kwargs : keyword arguments
            Keyword arguments directly passed to
            `~porchlight.door.DynamicDoor._base_function`.
        """
        self.update()
        result = super().__call__(*args, **kwargs)

        return result

    def call_without_update(self, *args, **kwargs) -> Any:
        """Executes the function stored in
        `~porchlight.door.DynamicDoor._base_function` *WITHOUT* executing
        `~porchlight.door.DynamicDoor.update()`

        Arguments
        ---------
        *args : positional arguments
            Arguments directly passed to
            `~porchlight.door.DynamicDoor._base_function`.

        **kwargs : keyword arguments
            Keyword arguments directly passed to
            `~porchlight.door.DynamicDoor._base_function`.
        """
        # Give a specific, useful message if self._base_function is not
        # initialized.
        if "_base_function" not in self.__dict__:
            msg = (
                "DynamicDoor does not contain _base_function attribute. "
                "Did you means to call DynamicDoor directly or with "
                "DirectDoor()?"
            )

            logger.error(msg)
            raise AttributeError(msg)

        result = self._base_function(*args, **kwargs)

        return result

    def __repr__(self):
        # Try generating a __str__ using the BaseDoor.__str__ method. If it
        # fails, then revert to an uninitialized DynamicDoor string as
        # appropriate.
        try:
            outstr = super().__repr__().replace("Door", "DynamicDoor")

        except AttributeError:
            outstr = "DynamicDoor(uninitialized)"

        return outstr

    def update(self):
        """Updates the DynamicDoor using `DynamicDoor._door_generator`

        This method is called when DynamicDoor.__call__ is invoked.
        """
        self._last_door = self._cur_door

        updated_door = self._door_generator(
            *self.generator_args, **self.generator_kwargs
        )

        if not isinstance(updated_door, BaseDoor):
            msg = f"Expected a BaseDoor object, but {updated_door} returned."
            logger.error(msg)
            raise TypeError(msg)

        # This is so incredibly sus... but it works for now. There is
        # definitely a more elegant way to do this.
        for attr, value in updated_door.__dict__.items():
            # Ignore all dunder attrs.
            if attr[:2] == "__":
                continue

            setattr(self, attr, value)

        self._cur_door = updated_door
