"""Tools for introspection of functions extending what :py:module:`inspect` can
do.
"""
import inspect

from typing import Callable, List, Tuple, Type


def get_all_source(function: Callable) -> Tuple[List[str], int]:
    """Retrieves all source code related to a given function, even if it has
    been otherwise wrapped.

    It returns a tuple containing a list of strings containing the source code
    and an integer (starting line number). This is output by the eventual call
    to `inspect.getsourcelines` on the wrapped function.

    Arguments
    ---------
    function : Callable
        A defined function to get the source code for.
    """
    if not isinstance(function, Callable):
        raise TypeError(
            f"Source lines can only be retrieved for Callable "
            f"objects, not {type(function)}."
        )

    if "__closure__" in dir(function) and function.__closure__:
        # Recursively dive down. the first closure cell value should be the
        # next function down.
        cell = function.__closure__[0].cell_contents

        if isinstance(cell, Callable) and not isinstance(cell, Type):
            return get_all_source(function.__closure__[0].cell_contents)

    sourcelines = inspect.getsourcelines(function)

    return sourcelines


def get_wrapped_function(function: Callable) -> Callable:
    """If the input callable has the `__closure__` attr and its first cell is a
    function, it will descend until it has found a callable object with no
    `__closure__` variable.
    """
    if not isinstance(function, Callable):
        raise TypeError(
            f"Only Callable objects may be unwrapped in this way, "
            f"not {type(function)}."
        )

    if "__closure__" in dir(function) and function.__closure__:
        # Recursively dive down. the first closure cell value should be the
        # next function down.
        cell = function.__closure__[0].cell_contents

        if isinstance(cell, Callable) and not isinstance(cell, Type):
            return get_wrapped_function(function.__closure__[0].cell_contents)

    return function
