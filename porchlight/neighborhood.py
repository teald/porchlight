import door
import param

from typing import Any, Callable, Dict, List


class Neighborhood:
    '''A neighborhood manages the interactions between Doors.'''

    _doors = Dict[str, door.Door]
    _params = Dict[str, param.Param]

    def __init__(self):
        '''Initializes the Neighborhood object.'''
        self._doors = {}

    def add_function(self, function: Callable):
        '''Adds a new function to the Neighborhood object.'''
        new_door = door.Door(function)

        self._doors[new_door.name] = new_door

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
        self._params.append(param.Param(parameter_name, value, constant))

    def call_all_doors(self):
        '''Attempts to call all doors currently in the neighborhood.'''
        # Check that all required parameters are represented.
        if not self.required_args_present():
            # TK REFACTORING temporary error type here.
            class ParameterMissingError(KeyError):
                pass

            raise ParameterMissingError(
                    f"Neighborhood object {self.__name__} cannot call all "
                    f"doors it contains."
                    )

        for cur_door in self._doors:
            req_kwargs = list(door.keyword_arguments.keys())
            req_args = [x for x in cur_door.arguments if x not in req_kwargs]

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
        if not all(pname in self._params for pname in self.required_params):
            return False

        return True

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
        all_required = []

        for _door in self.doors:
            all_required += _door.required_arguments

        return all_required


if __name__ == "__main__":
    neighborhood = Neighborhood()

    def test_fxn(x, y, z = 3) -> str:
        output = f"{x * y * z = }"
        return output

    neighborhood.add_function(test_fxn)

    import pdb; pdb.set_trace()
