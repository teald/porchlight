"""Defines the `Neighborhood` class."""
from . import door
from . import param
from .utils.typing_functions import decompose_type
from typing import Any, Callable, Dict, List, Union

import logging

logger = logging.getLogger(__name__)


class NeighborhoodError(Exception):
    pass


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

    _doors: Dict[str, door.Door]
    _params: Dict[str, param.Param]
    _call_order: List[str]

    def __init__(self, initial_doors: List[Callable] = []):
        self._doors = {}
        self._params = {}
        self._call_order = []

        for d in initial_doors:
            if isinstance(d, door.BaseDoor):
                self.add_door(d)

            else:
                self.add_function(d)

        # Logging
        msg = (
            f"Neighborhood initialized with {len(self._doors)} "
            f"doors/functions."
        )
        logger.debug(msg)

    def __repr__(self):
        # Must communicate the following:
        # + A unique identifier.
        # + List of doors
        # + list of tracked parameters and their values.
        info = {
            "doors": self.doors,
            "params": self.params,
            "call_order": self._call_order,
        }

        infostrs = [f"{key}={value}" for key, value in info.items()]

        outstring = f"Neighborhood({', '.join(infostrs)})"

        return outstring

    def add_function(
        self,
        function: Callable,
        overwrite_defaults: bool = False,
        dynamic_door: bool = False,
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

        dynamic_door : bool, optional
            If `True` (default `False`), then the output(s) of this `Door` will
            be converted into a `Door` or set of `Door`s in the `Neighborhood`
            object.
        """
        new_door = door.Door(function)
        logging.debug(f"Adding new function to neighborhood: {new_door.name}")

        self.add_door(new_door, overwrite_defaults, dynamic_door)

    def add_door(
        self,
        new_door: Union[door.Door, List[door.Door]],
        overwrite_defaults: bool = False,
        dynamic_door: bool = False,
    ):
        """Adds an already-initialized Door to the neighborhood.

        Parameters
        ----------
        new_door : :class:`~porchlight.door.Door`,
            :class:`~porchlight.door.DynamicDoor`, or :py:obj:`list` of
            :class:`~porchlight.door.Door` objects.

            Either a single initialized `door.Door` object or a list of them.
            If a list is provided, this function is called for each item in the
            list.

        overwrite_defaults : bool, optional
            If `True`, will overwrite any parameters shared between the
            `new_door` and `Neighborhood._params` to be equal to the defaults
            set by `new_door`. If `False` (default), no parameters that exist
            in the `Neighborhood` object already will be changed.

        dynamic_door : bool, optional
            If `True` (default `False`), then the output(s) of this `Door` will
            be converted into a `Door` or set of `Door`s in the `Neighborhood`
            object.
        """
        if isinstance(new_door, List):
            for nd in new_door:
                self.add_door(
                    nd,
                    overwrite_defaults=overwrite_defaults,
                    dynamic_door=dynamic_door,
                )

            return

        self._doors[new_door.name] = new_door

        # Add the new door to the call order.
        self._call_order.append(new_door.name)

        # Update the parameters as necesssary.
        # This will prefer default values passed by earlier doors.
        for pname, ptype in new_door.arguments.items():
            if pname not in self._params or overwrite_defaults:
                # This is a new parameter.
                parameter_name = pname
                value = param.Empty()

                if pname in new_door.keyword_args:
                    value = new_door.keyword_args[pname]

                self.add_param(parameter_name, value)

        # If not well-defined, we cannot modify outputs to this function.
        if not new_door.return_vals and not dynamic_door:
            return

        # Add all return values as parameters.
        if not dynamic_door:
            for pname in new_door.return_vals:
                if pname not in self._params:
                    self._params[pname] = param.Param(pname, param.Empty())

            return

        # Dynamic doors must be specified separately. They get initialized when
        # first called/explicitly generated.
        #
        # Dynamic doors must also be type-annotated.
        if (
            "return_types" not in new_door.__dict__
            or not new_door.return_types
        ):
            msg = (
                "DynamicDoor requires a type annotation for the "
                "function generator."
            )

            logger.error(msg)
            raise NeighborhoodError(msg)

        return_types = new_door.return_types

        for i, rt in enumerate(return_types):
            if isinstance(rt, door.Door) or rt is door.Door:
                ret_val = new_door.return_vals[i]
                if ret_val not in self.doors:
                    # Can define a function that just pulls out the attr
                    # independent of its current reference.
                    @door.DynamicDoor
                    def template_ddoor(param_name):
                        return getattr(self, "params")[param_name].value

                    # Need to rename this appropriately for the neighborhood.
                    # And provide a static copy of the current return value's
                    # name.
                    template_ddoor.name = ret_val
                    template_ddoor.generator_kwargs = {"param_name": ret_val}

                    self.add_door(template_ddoor)
                    self.add_param(ret_val, param.Empty())

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

    def get_value(self, parameter_name: str) -> Any:
        """Retrieves the value of a parameter by name. Does not return a Param
        object; it returns whatever data is stored in Param.value.

        Arguments
        ---------
        parameter_name : `str`
            The name of the parameter to retrieve the current value for.
        """
        return self._params[parameter_name].value

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
        self,
        parameter_name: str,
        value: Any,
        constant: bool = False,
        restrict: Union[Callable, None] = None,
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

        restrict : :py:class:`~typing.Callable` or None, optional
            Either a callable that returns something that can be evaluated to
            True or False, or None. Raises an error if the parameter is set to
            a value that fails the restriction check.

            For a full description, see the docs for
            :class:`~parameter.param.Param`.
        """
        if not isinstance(value, param.Param):
            new_param = param.Param(parameter_name, value, constant, restrict)

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
        :class:`~porchlight.door.Door`s are added to the `Neighborhood`.

        The way this is currently set up, it will not handle positional
        arguments. That is, if an input cannot be passed using its variable
        name, this will break.
        """
        # Need to call the doors directly.
        for doorname in self._call_order:
            # Dynamic doors must first be updated and parsed.
            if isinstance(self._doors[doorname], door.DynamicDoor):
                self._doors[doorname].update()

                # Need to ensure all params are present in the neighborhood.
                dynamic_params = self._doors[doorname].variables

                for p in (p for p in dynamic_params if p not in self._params):
                    # Check for a default value here.
                    if p in self._doors[doorname].keyword_args:
                        value = self._doors[doorname].keyword_args[p]

                    else:
                        value = param.Empty

                    self.add_param(p, value)

            cur_door = self._doors[doorname]
            req_params = cur_door.arguments
            input_params = {}

            for pname in req_params:
                input_params[pname] = self._params[pname].value

            # Run the cur_door object and catch its output.
            logging.debug(f"Calling door {cur_door.name}.")
            output = cur_door(**input_params)

            # Check if the cur_door has a known return value.
            if not cur_door.return_vals:
                logging.debug("No return value found.")
                continue

            elif len(cur_door.return_vals) > 1:
                update_params = {
                    v: x for v, x in zip(cur_door.return_vals, output)
                }

            else:
                update_params = {cur_door.return_vals[0]: output}

            logging.debug(f"Updating parameters: {list(update_params.keys())}")

            # Update all parameters to reflect the next values.
            for pname, new_value in update_params.items():
                # If the parameter is currently empty, just reassign and
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

                self._params[pname].value = new_value

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
            a key in `Neighborhood._doors`.
        """
        # The order list must:
        #  + Contain all doors once.
        #  + All doors must already exist and be known.
        if not order:
            msg = f"Empty or invalid input: {order}."
            logger.error(msg)
            raise ValueError(msg)

        elif len(order) > len(self._doors):
            msg = (
                f"More labels provided than doors "
                f"({len(order)} labels vs {len(self._doors)} doors)."
            )
            logger.error(msg)
            raise ValueError(msg)

        elif any(n not in self._doors for n in order):
            i = [n not in self._doors for n in order].index(True)

            msg = f"Could not find door with label: {order[i]}"
            logger.error(msg)
            raise KeyError(msg)

        logging.debug(f"Adjusting call order: {self._call_order} -> {order}")

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
        return self._params

    @property
    def required_parameters(self):
        """Defines parameters that must not be empty at the start of a run
        for the run to successfully execute.
        """
        req_args = set()
        returned_args = set()

        for d in self._doors.values():
            for pname in d.required_arguments:
                if pname not in returned_args:
                    req_args.add(pname)

                # Add returned values that would now be initialized. This is
                # assuming that all returns will successfully.
                for ra in d.return_vals:
                    for p in ra:
                        returned_args.add(p)

        return req_args

    @property
    def uninitialized_inputs(self):
        """Parameters that are inputs to Doors within this Neighborhood with
        Empty values.
        """
        input_args = []

        for d in self._doors.values():
            for pname in d.required_arguments:
                if (
                    pname not in input_args
                    and self._params[pname].value == param.Empty()
                ):
                    input_args.append(pname)

        return input_args
