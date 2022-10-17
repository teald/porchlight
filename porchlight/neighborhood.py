"""Defines the `Neighbor` class."""
from . import door
from . import param

from typing import Any, Callable, Dict, List, Union

import logging

logger = logging.getLogger(__name__)


class Neighborhood:
    """A neighborhood manages the interactions between Doors. It consists of a
    modifiable collection of :class:`~porchlight.door.Door` (or
    :class:`~porchlight.door.BaseDoor`) objects.

    Attributes
    ----------
    _doors : :py:obj:`dict`, :py:obj:`str`: :class:`~porchlight.door.Door`
        Contains all data for :class:`~porchlight.door.Door` objects. The keys
        are, by default, the :meth:`~porchlight.door.Door.name`
        property for the corresponding :class:`~porchlight.door.Door` values.

    _params : :py:obj:`dict`, :py:obj:`str`: :class:`~porchlight.param.Param`
        Contains all the parameters currently known to and managed by the
        :class:`~porchlight.neighborhood.Neighborhood` object.

    _call_order : :py:obj:`list`, :py:obj:`str`
        The order in which the :class:`~porchlight.door.Door` objects in
        `_doors` are called. By default, this is the order in which
        :class:`~porchlight.door.Door`s are added to the `Neighborhood`.
    """

    _doors: Dict[str, param.Param]
    _params: Dict[str, param.Param]
    _call_order: List[str]

    def __init__(self):
        """Initializes the Neighborhood object."""
        self._doors = {}
        self._params = {}
        self._call_order = []

    def add_function(
        self, function: Callable, overwrite_defaults: bool = False
    ):
        """Adds a new function to the Neighborhood object.

        Parameters
        ----------
        function : Callable
            The function to be added. This is converted to a
            :class:`~porchlight.door.Door` object by this method.

        overwrite_defaults : bool, optional
            If `True`, will overwrite any parameters shared between the
            `function` and `Neighborhood._params` to be equal to the defaults
            set by `function`. If `False` (default), no parameters that exist
            in the `Neighborhood` object already will be changed.
        """
        new_door = door.Door(function)

        self.add_door(new_door, overwrite_defaults)

    def add_door(
        self,
        new_door: Union[door.Door, List[door.Door]],
        overwrite_defaults: bool = False,
    ):
        """Adds an already-initialized Door to the neighborhood.

        Parameters
        ----------
        new_door : :class:`~porchlight.door.Door` or :py:obj:`list` of
            :class:`~porchlight.door.Door` objects. Either a single initialized
            `door.Door` object or a list of them.  If a list is provided, this
            function is called for each item in the list.

        overwrite_defaults : bool, optional
            If `True`, will overwrite any parameters shared between the
            `new_door` and `Neighborhood._params` to be equal to the defaults
            set by `new_door`. If `False` (default), no parameters that exist
            in the `Neighborhood` object already will be changed.
        """
        if isinstance(new_door, List):
            for nd in new_door:
                self.add_door(nd, overwrite_defaults=overwrite_defaults)

            return

        self._doors[new_door.name] = new_door

        # Add the new door to the call order.
        self._call_order.append(new_door.name)

        # Update the parameters as necesssary.
        # This will prefer default values passed by earlier
        for pname, ptype in new_door.arguments.items():
            if pname not in self._params or overwrite_defaults:
                # This is a new parameter.
                parameter_name = pname
                value = param.Empty()

                if pname in new_door.keyword_args:
                    value = new_door.keyword_args[pname]

                self.add_param(parameter_name, value)

        # If not well-defined, we cannot modify outputs to this function.
        if not new_door.return_vals:
            return

        for pname in [p for rvs in new_door.return_vals for p in rvs]:
            if pname not in self._params:
                self._params[pname] = param.Param(pname, param.Empty())

    def remove_door(self, name: str):
        """Removes a :class:`~porchlight.door.Door` from :attr:`_doors`.

        Parameters
        ----------
        name : :py:obj:`str`
            The name of the :class:`~porchlight.door.Door` to be removed. It
            must correspond to a key in `Neighborhood._doors` attribute.

        Raises
        ------
        KeyError
            If `name` is not present in `_doors` attribute.
        """
        if name not in self._doors:
            raise KeyError(f"Could not find a door named {name}.")

        del self._doors[name]

    def set_param(
        self,
        parameter_name: str,
        new_value: Any,
        constant: bool = False,
        *,
        ignore_constant: bool = False,
    ) -> param.Param:
        """Set the value of a parameter to a new value. Since parameters are
        not meant to be modified like this right now, generate a new parameter.

        Parameters
        ----------
        parameter_name : :py:obj:`str`
            The name of the parameter to modify.

        new_value : `Any`
            The value to be assigned to this parameter.

        constant : :py:obj:`bool`
            Will be passed to :class:`~porchlight.param.Param` as the
            `constant` keyword argument.

        ignore_constant : :py:obj:`bool`, optional, keyword-only
            When assigning this parameter, it will ignore the `constant`
            attribute of the current parameter.

        Raises
        ------
        :class:`~porchlight.param.ParameterError`
            Is raised if the parameter attempting to be changed has `True` for
            its `constant` attribute. Will not be raised by this method if
            `ignore_constant` is `True`.
        """
        _old_param = self._params[parameter_name]

        if not ignore_constant and _old_param.constant:
            msg = f"Parameter {_old_param.name} is set to constant."

            logger.error(msg)

            raise param.ParameterError(msg)

        self._params[parameter_name] = param.Param(
            parameter_name, new_value, constant
        )

    def add_param(
        self, parameter_name: str, value: Any, constant: bool = False
    ):
        """Adds a new parameter to the `Neighborhood` object.

        The parameters all correspond to arguments passed directly to the
        :class:`~porchlight.param.Param` initializer.

        Parameters
        ----------
        parameter_name : :py:obj:`str`
            Name of the parameter being created.

        value : `Any`
            Parameter value

        constant : :py:obj:`bool`, optional
            If `True`, the parameter is set to constant.
        """
        if not isinstance(value, param.Param):
            new_param = param.Param(parameter_name, value, constant)

        else:
            new_param = value

        self._params[parameter_name] = new_param

    def required_args_present(self) -> bool:
        """Returns True if all the necessary arguments to run all Doors in the
        Neighborhood object are included in the Neighborhood object.
        """
        done = []
        for d_params in (d.arguments for d in self.doors.values()):
            for pname in d_params:
                if pname in done:
                    continue

                done.append(pname)

                pname_missing = pname not in self._params
                is_empty_param = False

                if not pname_missing:
                    is_empty_param = isinstance(
                        self._params[pname].value, param.Empty
                    )

                if pname_missing or is_empty_param:
                    return False

        return True

    def call_all_doors(self):
        """Calls every door currently present in the neighborhood object.

        This order is currently dictated by the order in which
        :class:`~parameter.door.Door`s are added to the `Neighborhood`.

        The way this is currently set up, it will not handle positional
        arguments. That is, if an input cannot be passed using its variable
        name, this will break.
        """
        # Need to call the doors directly.
        for doorname in self._call_order:
            cur_door = self._doors[doorname]
            req_params = cur_door.arguments
            input_params = {}

            for pname in req_params:
                input_params[pname] = self._params[pname].value

            # Run the cur_door object and catch its output.
            # TK TODO: include support for positional-only arguments.
            output = cur_door(**input_params)

            # Check if the cur_door has a known return value.
            if not cur_door.return_vals:
                continue

            elif len(cur_door.return_vals[0]) > 1:
                # TK REFACTORING this only works for functions with one
                # possible output. This, frankly, should probably be the case
                # nearly all of the time. Still need to make a call on if
                # there's support in a subset of cases.
                update_params = {
                    v: x for v, x in zip(cur_door.return_vals[0], output)
                }

            else:
                assertmsg = "Mismatched output/return."
                assert len(cur_door.return_vals) == 1, assertmsg
                update_params = {cur_door.return_vals[0][0]: output}

            for pname, new_value in update_params.items():
                # If ther parameter is currently empty, just reassign and
                # continue. This refreshes the type value of the parameter
                if isinstance(self._params[pname].value, param.Empty):
                    self._params[pname] = param.Param(pname, new_value)

                # If the parameter is supposed to be constant, raise an error.
                if pname in self._params and self._params[pname].constant:
                    msg = (
                        f"Door {cur_door.name} is attempting to change a "
                        f"constant parameter: {pname}."
                    )

                    logger.error(msg)
                    raise param.ParameterError(msg)

                # Editing the _value directly here... but I'm not sure if
                # that's the best idea.
                self._params[pname]._value = new_value

    def run_step(self):
        """Runs a single step forward for all functions, in specified order,
        based on the current parameter state of the Neighborhood object.

        The way this is currently set up, it will not handle positional
        arguments. That is, if an input cannot be passed using its variable
        name, this will break.
        """
        # Ensure that all required parameters are defined.
        empty_params = self.empty_parameters
        req_args = self.required_parameters

        if any(e in req_args for e in empty_params):
            missing = [e for e in empty_params if e in req_args]
            msg = f"Missing parameters required for input: {missing}."
            logger.error(msg)
            raise param.ParameterError(msg)

        self.call_all_doors()

    def order_doors(self, order: List[str]):
        """Allows the doors to be ordered when called.

        If this is never called, the call order will be equivalent to the order
        in which the doors are added to the `Neighborhood`. As of right now,
        all doors present must be included in the `order` argument or a
        `KeyError` will be thrown.

        Arguments
        ---------
        order : :py:obj:`list`, str
            The order for doors to be called in. Each `str` must correspond to
            a key in `Neighborhood._doors` at the time of calling this
            method.
        """
        if any(n not in self._doors for n in order):
            i = [n not in self._doors for n in order].index(True)
            raise KeyError(f"Could not find door with label: {order[i]}")

        self._call_order = order

    @property
    def doors(self):
        return self._doors

    @property
    def empty_parameters(self):
        empty_params = {}

        for pname, p in self._params.items():
            if isinstance(p.value, param.Empty):
                empty_params[pname] = p

        return empty_params

    @property
    def parameters(self):
        return self._params

    @property
    def params(self):
        return self.parameters

    @property
    def required_parameters(self):
        """Defines parameters that must not be empty at the start of a run
        for the run to successfully execute.
        """
        # TK TODO need to anticipate what parameters are returned during
        # run_step.
        req_args = []

        for d in self._doors.values():
            for pname in d.required_arguments:
                if pname not in req_args:
                    req_args.append(pname)

        return req_args
