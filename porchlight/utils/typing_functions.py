import typing
import logging

logger = logging.getLogger(__name__)


def decompose_type(
    typevar: typing.Type,
    break_types: typing.List[typing.Type] = [],
    include_base_types: bool = True,
) -> typing.List[typing.Type]:
    """Decomposes a single type that takes arguments and returns a list
    containing all types referenced within, recursively.

    Arguments
    ---------
    typevar : `~typing.Type`
        type annotation to decompose.

    break_types : `~typing.List[~typing.Type]`, optional
        If a list of types is provided, instances of this particular type will
        always halt the decomposition process. So, for example, if break_types
        = [Callable], and typevar = Callable[str, float], then all_types
        (return value) = [Callable[str, float]]

    include_base_types : :py:obj:`bool`, optional
        If `False` (default `True`), base types containing other relevant types
        are ignored. These are only for *resolvable* types at return, such as
        Tuples, Lists, and Iterables. Callables are excluded by default.
    """
    all_types = []

    # Check that typevar is not one of interest to any of the types in
    # break_types.
    base_type = typing.get_origin(typevar)

    for bt in break_types:
        if base_type == typing.get_origin(bt):
            return [typevar]

    # If there are internal arguments (i.e., in brackets like List[str, ...])
    # then the type can be further decomposed.
    try:
        if "__args__" in typevar.__dict__:
            # Do not do this for callables, since their arguments and return
            # types are not accessible at the time they are returned.
            if (
                base_type == typing.get_origin(typing.Callable)
                or not typevar.__args__
            ):
                return [typevar]

            if include_base_types:
                all_types += [typevar]

            for arg in typevar.__args__:
                all_types += decompose_type(arg, break_types)

        else:
            all_types = [typevar]

    except AttributeError as e:
        # This should only be allowed if typevar does not have a __dict__ attr,
        # in which case we assume that this is a user-defined type.
        try:
            typevar.__dict__
            raise e

        except AttributeError:
            all_types = [typevar]

            # Log this.
            logger.debug(
                f"Return type parsed allowed without __dict__: {typevar}"
            )

    return all_types
