import inspect
import pdb
import logging

logger = logging.getLogger(__name__)

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

        logger.info(f"Initialized Door() object successfully at {self}")
        if self.debug:
            print(f"Initialized Door object {self} successfully.")

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
            self.model_type = 'method'

        else:
            raise DoorError(f"Object {self.input_object} not recognized as a "
                            f"function or class (type "
                            f"{type(self.input_object)})"
                            )

        # Get information using inspect.
        self.info = inspect.getmembers(self.input_object)

        # If a class, get all possible attributes using string matching.
        self._inspect_source_code()

    def _inspect_source_code(self):
        '''Inspects the source code of teh class or function definition using
        inspect.getsource().
        '''
        source_code = inspect.getsource(self.input_object).split('\n')

        # Get function return statements
        if self.model_type == 'function':
            for i, l in enumerate(source_code):
                # Check for return statement
                if 'return' == l.strip().split(' ')[0]:
                    self.returns = [x.strip() for x in l.split('.')[1:]]

        # Get class information not gathered by inspect
        elif self.model_type == 'class':
            possible_attrs = []

            for i, l in enumerate(source_code):
                match l.strip().split():
                    case ['def', *definition]:
                        # Check if this is really a method or a local
                        # definition
                        if 'self' not in ''.join(definition):
                            logging.debug(f"Non-method passed at {i}: "
                                          f"{''.join(definition)}"
                                          )
                            continue

                        else:
                            # This analysis will entirely fail in the rpesense
                            # of comments or one-line definitions (god forbid).
                            args = definition[1:]
                            args = [a.replace(',', '') for a in args]
                            args = [a.replace('):', '') for a in args]

                            pdb.set_trace()
                            logging.debug(f"Found a method definition at {i} "
                                          f" for ."
                                          )

                    case ['class', *class_info]:
                        # Already have the class name information.
                        logger.debug(f"Passed class name at {i}.")
                        continue

                    case [assignment, '=', value]:
                        # Check if this is a possible attribute assignment
                        if 'self.' == assignment[:5]:
                            attr_name = ''.join(assignment.split('.')[1:])
                            possible_attrs.append(attr_name)

                            logger.debug(f"Suspected possible attr found: "
                                         f"{attr_name}.")

                        else:
                            logger.debug(f"Possible attribute passed at {i}: "
                                         f"{l}"
                                         )

                    case []:
                        # Empty line
                        logger.debug(f"Empty line at {i}.")
                        continue

                    case _:
                        # Something else
                        logger.warning(f"Line {i} was not handled as a "
                                       f"class property when split: "
                                       f"{l.split()}"
                                       )

                self.possible_attrs = possible_attrs

        else:
            logger.error(f"{self} ran into an error attempting to resolve "
                         f"the source code with {self.model_type = }."
                         )
            raise DoorError(f"Type not recognized (type is "
                            f"{type(self.model_type)})."
                            )

        logger.info(f"Source code parsed for {self.input_object.__name__}.")

def __unit_test():
    '''Tests the definitions/classes/methods in this file.'''
    logger.info(f"Beginning unit test for {__name__}")

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
    test_door = Door(TestClass, debug=True)

    # Test for a method alone
    pass

    # Test for a function
    pass

    logger.info(f"Concluding unit test for {__name__}.")


if __name__ == "__main__":
    __unit_test()
