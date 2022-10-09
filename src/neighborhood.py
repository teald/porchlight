import door
import param

from typing import Any, Callable, Dict, List

import logging


# logger = logging.getLogger(__name__)
if not logging.getLogger().hasHandlers():
    logging.basicConfig(filename=f"neighborhood.log")
    logger = logging.getLogger(__name__)

else:
    logger = logging.getLogger()


class Neighborhood:
    '''A neighborhood manages the interactions between Doors.'''

    _doors:  Dict[str, door.Door]
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
                value = param.empty

                if pname in new_door.keyword_args:
                    value = new_door.keyword_args[pname]

                self.add_param(parameter_name, value)

    def remove_door(self, name: str):
        '''Removes a door from the Neighborhood.'''
        if name not in self._doors:
            raise KeyError(f"Could not find a door named {name}.")

        del self._doors[name]

    def add_param(self,
                  parameter_name: str,
                  value: Any,
                  constant: bool = False
                  ):
        '''Adds a new parameter to the Neighborhood'''
        new_param = param.Param(parameter_name, value, constant)
        self._params[parameter_name] = new_param

    def call_all_doors(self):
        '''Attempts to call all doors currently in the neighborhood.'''
        # Check that all required parameters are represented.
        if not self.required_args_present():
            # TK REFACTORING temporary error type here.
            class ParameterMissingError(KeyError):
                pass

            msg = (f"Neighborhood object {self.__name__} cannot call all "
                   f"doors it contains. There is at least one missing "
                   f"parameter."
                   )

            logging.error(msg)
            raise ParameterMissingError(msg)

        for cur_door in self._doors:
            req_kwargs = list(door.keyword_arguments.keys())
            req_args = [x for x in cur_door.arguments if x not in req_kwargs]

            # Positional arguments currently do nothing. Positional-only
            # arguments are not resolvable in porchlight yet, (see run_step)
            pos_args = []
            for arg in req_args:
                pos_args.append(self._params[arg].value)

            kw_args = {}
            for arg in req_args:
                kw_args[arg] = self._params[arg].value

            # Call the door object with all known args
            outputs = cur_door(*pos_args, **kw_args)

            if outputs is None:
                continue

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

                if (pname not in self._params
                    or isinstance(self._params[pname].value, param.Empty)
                    ):
                    return False

        return True

    def run_step(self):
        '''Runs a single step forward for all functions, in specified order,
        based on the current parameter state of the Neighborhood object.

        The way this is currently set up, it will not handle positional
        arguments. That is, if an input cannot be passed using its variable
        name, this will break.
        '''
        # Need to call the doors directly.
        for door in self._doors.values():
            req_params = door.arguments
            params = {}

            for pname in req_params:
                params[pname] = self._params[pname].value

            # Run the door object and catch its output.
            output = door(**params)

            # Check if the door has a known return value.
            if door.return_vals is None:
                continue

            if isinstance(output, tuple):
                update_params = {v: x for v, x in zip(door.return_vals, output)}

            else:
                assert len(door.return_vals) == 1, "Mismatched output and return."
                update_params = {door.return_vals[0]: output}

            for pname, new_value in update_params.items():
                # If the parameter is supposed to be constant, raise an error.
                if pname in self._params and self._params[pname].constant:
                    msg = (f"Door {door.name} is attempting to change a "
                           f"constant parameter: {pname}."
                           )

                    log.error(msg)
                    raise param.ParamError(msg)

                # Editing the _value directly here... but I'm not sure if
                # that's the best idea.
                if pname in self._params:
                    self._params[pname]._value = new_value

                else:
                    # Adding the parameter, is this reasonable?
                    self._params[pname] = param.Param(pname, new_value)

    def __str__(self):
        outstr = "Neighborhood object:\n"

        # Parameters
        outstr += "  Parameters:\n"
        for pname, pob in self._params.items():
            value = pob.value
            outstr += f"    {pname}: {value}\n"

        # Included functions.
        outstr += "\n  Functions:\n"

        for door in self.doors.values():
            name = door.name
            outstr += f"    {name}()\n"

        return outstr


    @property
    def doors(self):
        return self._doors

    @property
    def door_names(self):
        return [name for name in self._doors]

    @property
    def params(self):
        return self._params

    @property
    def required_params(self) -> List[str]:
        all_required = set()

        for door in self.doors.values():
            for pname, val in door.keyword_args.items():
                if isinstance(val, param.Empty):
                    all_required.add(pname)

        return list(all_required)

if __name__ == "__main__":
    neighborhood = Neighborhood()

    def test_fxn(x, y, z = 3) -> str:
        output = x * y * z
        return output

    print("Adding test_fxn")
    neighborhood.add_function(test_fxn)

    print(f"{neighborhood.required_args_present() = }")

    x = {
            'parameter_name': 'x',
            'value': 1
            }
    y = {
            'parameter_name': 'y',
            'value': 5
            }

    neighborhood.add_param(**x)
    neighborhood.add_param(**y)

    print(f"{neighborhood.required_args_present() = }")

    neighborhood.run_step()
    print(f"{neighborhood.params['x'].value = }")
    print(f"{neighborhood.params['y'].value = }")
    print(f"{neighborhood.params['z'].value = }")
    print(f"{neighborhood.params['output'].value = }")

    # Define another function to add.
    def update_x(output) -> int:
        '''Test function that will attempt to take one parameter and update
        another.
        '''
        x = output**2
        return x

    print("Adding update_x")
    neighborhood.add_function(update_x)
    print(f"{neighborhood.required_args_present() = }")
    print(f"{neighborhood.params['x'].value = }")
    print(f"{neighborhood.params['y'].value = }")
    print(f"{neighborhood.params['z'].value = }")
    print(f"{neighborhood.params['output'].value = }")

    neighborhood.run_step()

    print(neighborhood)

    import pdb; pdb.set_trace()
