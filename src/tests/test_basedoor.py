'''Tests to verify the integrity of the porchlight.door.BaseDoor class and any
relevant helper functions or objects.
'''
from unittest import TestCase

from door import BaseDoor
from param import Empty, ParameterError


class TestBaseDoor(TestCase):
    def test___init__(self):
        def test_fxn(x: int) -> int:
            y = 2 * x
            return y

        door = BaseDoor(test_fxn)

        # Must contain both input and output parameter.
        arguments = ['x']
        keyword_args = ['x']
        return_vals = [['y']]

        # Not comparing any values during this test.
        for arg in arguments:
            self.assertIn(arg, door.arguments)

        for kwarg in keyword_args:
            self.assertIn(kwarg, door.keyword_args)

        for retval in return_vals:
            self.assertIn(retval, door.return_vals)

        # Call the BaseDoor
        result = door(x=5)

        self.assertEqual(result, 10)

        # Decorators (with defaults) should behave as expected
        @BaseDoor
        def fxn_use_decorator(x):
            z = 2 * x
            return z

        self.assertEqual(fxn_use_decorator(10), 20)

        self.assertEqual(fxn_use_decorator.name,
                         "fxn_use_decorator"
                         )

        self.assertEqual(fxn_use_decorator.arguments, {'x': Empty})

    def test___call__(self):
        def test_fxn(x: int) -> int:
            y = 2 * x
            return y

        door = BaseDoor(test_fxn)

        # Call the BaseDoor with erroneous types based on annotations.
        with self.assertRaises(ParameterError):
            result = door(x='6')

    def test__get_return_vals(self):
        # Should be able to handle one return val.
        def fxn_one_return(x):
            return y

        result = BaseDoor._get_return_vals(fxn_one_return)

        self.assertEqual(result, [['y']])

        # Multiple return values, no inputs
        def fxn_no_inputs():
            return x, y, z

        result = BaseDoor._get_return_vals(fxn_no_inputs)

        self.assertEqual([['x', 'y', 'z']], result)

        # No-return function.
        def fxn_no_return(x, y):
            pass

        result = BaseDoor._get_return_vals(fxn_no_return)

        self.assertEqual([], result)

        # Specified return types.
        def fxn_return_types(x: int, y) -> str:
            outstr = f"{x} || {y}"
            return outstr

        result = BaseDoor._get_return_vals(fxn_return_types)

        self.assertEqual([['outstr']], result)

if __name__ == "__main__":
    unittest.main()
