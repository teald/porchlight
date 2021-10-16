import inspect
import pdb


class DoorError(Exception):
    pass

class Door:
    '''The Door class is the primary 'model' or 'module' class of porchlight.
    It accesses functions and classes passed to it and parses it for metadata
    to use for coupling.
    '''

    def __init__(self, input_object, debug=True):
        '''Initializes the Door class.

        Arguments:
            + input_object (function or object): an object or function
                definition to be assessed and stored by the Door instance.
            + debug (bool, default True): turns debugging on if True, off if
                False
        '''
        # Assert input types
        assert isinstance(debug, bool), "debug must be a boolean value."

        self.input_object = input_object
        self.debug = debug

        # Initialization setup.
        # Get the metadata directly accessible from the inspect module.
        self._inspect_input_object()

    def _inspect_input_object(self):
        '''Inspects the object passed to the Door initialization and pulls
        information about the arguments, return values, and other things.
        '''
        # Determine if the object is a function or a class.
        if inspect.isclass(self.input_object):
            self.model_type = 'class'

        elif inspect.isfunction(self.input_object):
            self.model_type = 'function'

        elif inspect.ismethod(self.input_object):
            sef.model_type = 'method'

        else:
            raise DoorError(f"Object {self.input_object} not recognized as a "
                            f"function or class (type "
                            f"{type(self.input_object)})"
                            )

        # Get information using inspect.
        self.info = inspect.getmembers(self.input_object)

def unit_test():
    '''Tests the definitions/classes/methods in this file.'''
    class TestClass:
        '''Just an example class for the unit test.'''
        def __init__(self, x, y, z = 'r'):
            self.x = x
            self.y = y
            self.z = z

            self.generated = True

        def a_method(self, a, b):
            output_1 = a + self.x
            output_2 = b + self.z

            combined_output = output_1 + output_2
            return output_1, output_2

    # Test Door initialization
    print(f"Testing door initialization... ", end='')

    try:
        test_door = Door(TestClass, debug=False)

    except:
        print("failed!")
        raise

    print(f"finished.")

    for name, _type in test_door.info:
        print(f"{name}:".ljust(15) + str(_type))


if __name__ == "__main__":
    unit_test()
