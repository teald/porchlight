import inspect
import logging
import string

from typing import Any, Callable, Dict, List, Type


logger = logging.getLogger(__name__)


class BaseDoor:
    '''Contains the basic information of a Door object, as well as base
    functions.
    '''
    _base_function: Callable
    arguments: Dict[str, Type]
    keyword_args: Dict[str, Any]
    max_n_return: int
    min_n_return: int
    n_args: int
    name: str
    return_vals: List[List[str]]

    def __init__(self, function: Callable):
        '''Initializes the BaseDoor class. It takes any callable (function,
        lambda, method...) and inspects it to get at its arguments and
        structure.
        '''
        self._base_function = function
        self._inspect_base_callable()

    def _inspect_base_callable(self):
        '''Inspect the BaseDoor's baseline callable for primary attributes.'''
        function = self._base_function

        self.name = function.__name__
        self.arguments = {}

        for name, param in inspect.signature(function).parameters.items():
            self.arguments[name] = param.annotation

        # Replace the inspect._empty values with typings.Any, which is a bit
        # more universal/descriptive, especially for some functions where it
        # does its own type handling.
        for name, _type in self.arguments.items():
            if _type == inspect._empty:
                self.arguments[name] = Any

        self.n_args = len(self.arguments)

        # The return values require some more effort.
        self.return_vals = self._get_return_vals(function)

        logging.debug(
                f"Found {self.n_args} arguments in {self.name}."
                )

    def __call__(self, *args, **kwargs):
        '''Calls the BaseDoor's function as normal.

        The keys of kwargs must be passed with the same name as variables
        within the BaseDoor. As of right now, if *extra* values are included,
        they are ignored.
        '''
        input_kwargs = {k: v for k, v in kwargs.items() if k in self.arguments}

        return self._base_function(*args, **input_kwargs)

    @staticmethod
    def _get_return_vals(function: Callable) -> List[str]:
        '''Gets the names of the return value variables for a given
        function.
        '''
        lines, start_line = inspect.getsourcelines(function)

        # These characters signal that the return statement does not contain
        # any operations on the return values, which is undefined for the
        # purposes of the BaseDoor
        allowed_chars = (
                string.ascii_letters
                + string.digits
                + '_'
                )

        return_vals = []

        for i, line in enumerate(lines):
            if 'return' in line:
                # This is a set of possible return values.
                line = line.strip()[len('return') + 1:]
                vals = line.split(',')

                return_vals.append([v.strip() for v in vals])

                for val in return_vals:
                    if any(c not in allowed_chars for c in val):
                        # This is undefined, not an error. So assign return
                        # value 'undefined' for this return statement and issue
                        # a warning.
                        logging.warning(
                                f"Could not define any set of return variable "
                                f"names for the following return line: \n"
                                f"{start_line+i}) {line.strip()}\n"
                                f"While not crucial to this function, be "
                                f"aware that this means no return value will "
                                f"be modified by this callable."
                                )

                        return_vals.append(None)

        return return_vals


class Door(BaseDoor):
    def __init__(self):
        logger.error("Door class has not been implemented.")
        raise NotImplementedError("Door class has not been implemented.")


if __name__ == "__main__":
    # Testing
    def test(x: int, y, z: int = 8) -> int:
        x = x * y * z
        return x

    door = BaseDoor(test)

    print(f"{door(1, 2, z = 3) = }")

    import pdb; pdb.set_trace()
