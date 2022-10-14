import door
import param

from typing import Any, Callable, Dict, List

import logging
logger = logging.getLogger(__name__)


class Neighborhood:
    '''A neighborhood manages the interactions between Doors.'''
    _doors: Dict[str, param.Param]
    _params: Dict[str, param.Param]

    def __init__(self):
        '''Initializes the Neighborhood object.'''
        self._doors = {}
        self._params = {}

    def add_function(self,
                     function: Callable,
                     overwrite_defaults: bool = False
                     ):
        '''Adds a new function to the Neighborhood object.'''
        new_door = door.Door(function)

        self._doors[new_door.name] = new_door

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

        for pname in [p[0] for p in new_door.return_vals]:
            if pname not in self._params:
                value = param.Empty()
                self.add_param(pname, value)

    def add_door(self,
                 new_door: door.Door | List[door.Door],
                 overwrite_defaults: bool = False
                 ):
        '''Adds an already-initialized Door to the neighborhood.'''
        if isinstance(new_door, List):
            for nd in new_door:
                self.add_door(
                        nd,
                        overwrite_defaults=overwrite_defaults
                        )

            return

        self._doors[new_door.name] = new_door

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
        '''Removes a door from the Neighborhood.'''
        if name not in self._doors:
            raise KeyError(f"Could not find a door named {name}.")

        del self._doors[name]

    def set_param(self,
                  parameter_name: str,
                  new_value: Any,
                  constant: bool = False,
                  *,
                  ignore_constant: bool = False
                  ) -> param.Param:
        '''Set the value of a parameter to a new value. Since parameters are
        not meant to be modified like this, generate a new parameter.
        '''
        _old_param = self._params[parameter_name]

        if not ignore_constant and _old_param.constant:
            msg = f"Parameter {_old_param.name} is set to constant."

            logger.error(msg)

            raise param.ParameterError(msg)

        self._params[parameter_name] = param.Param(parameter_name,
                                                   new_value,
                                                   constant
                                                   )

    def add_param(self,
                  parameter_name: str,
                  value: Any,
                  constant: bool = False
                  ):
        '''Adds a new parameter to the Neighborhood'''
        if not isinstance(value, param.Param):
            new_param = param.Param(parameter_name, value, constant)

        else:
            new_param = value

        self._params[parameter_name] = new_param

    def required_args_present(self) -> bool:
        '''Returns True if all the necessary arguments to run all Doors in the
        Neighborhood object are included in the Neighborhood object.
        '''
        done = []
        for d_params in (d.arguments for d in self.doors.values()):
            for pname in d_params:
                if pname in done:
                    continue

                done.append(pname)

                pname_missing = pname not in self._params

                if not pname_missing:
                    is_empty_param = isinstance(self._params[pname].value,
                                                param.Empty
                                                )

                else:
                    # Parameter cannot be Empty if it is missing.
                    is_empty_param = False

                if pname_missing or is_empty_param:
                    return False

        return True

    def call_all_doors(self):
        '''Calls every door currently present in the neighborhood object in
        current list order.
        '''
        # Need to call the doors directly.
        for cur_door in self._doors.values():
            req_params = cur_door.arguments
            input_params = {}

            for pname in req_params:
                input_params[pname] = self._params[pname].value

            # Run the cur_door object and catch its output.
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
                    msg = (f"Door {cur_door.name} is attempting to change a "
                           f"constant parameter: {pname}."
                           )

                    logger.error(msg)
                    raise param.ParameterError(msg)

                # Editing the _value directly here... but I'm not sure if
                # that's the best idea.
                self._params[pname]._value = new_value

    def run_step(self):
        '''Runs a single step forward for all functions, in specified order,
        based on the current parameter state of the Neighborhood object.

        The way this is currently set up, it will not handle positional
        arguments. That is, if an input cannot be passed using its variable
        name, this will break.
        '''
        # Ensure that all required parameters are defined.
        empty_params = self.empty_parameters
        req_args = self.required_parameters

        if any(e in req_args for e in empty_params):
            missing = [e for e in empty_params if e in req_args]
            msg = f"Missing parameters required for input: {missing}."
            logger.error(msg)
            raise param.ParameterError(msg)

        self.call_all_doors()

    @property
    def empty_parameters(self):
        empty_params = {}

        for pname, p in self._params.items():
            if isinstance(p.value, param.Empty):
                empty_params[pname] = p

        return empty_params

    @property
    def doors(self):
        return self._doors

    @property
    def parameters(self):
        return self._params

    @property
    def params(self):
        return self.parameters

    @property
    def required_parameters(self):
        '''Defines parameters that must not be empty at the start of a run.

        TK TODO: Need to anticipate what parameters are returned during
        run_step.
        '''
        req_args = []

        for d in self._doors.values():
            for pname in d.required_arguments:
                if pname not in req_args:
                    req_args.append(pname)

        return req_args
