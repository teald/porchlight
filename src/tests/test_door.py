'''Tests to verify the integrity of the porchlight.door.Door class and any
relevant helper functions or objects.
'''
from unittest import TestCase

from door import Door
from param import Empty, ParameterError

import logging
import os
logging.basicConfig(filename=f"{os.getcwd()}/porchlight_unittest.log")

class TestDoor(TestCase):
    def test___init__(self):
        def test_fxn(x: int) -> int:
            y = 2 * x
            return y

        door = Door(test_fxn)

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

        # Call the Door
        result = door(x=5)

        self.assertEqual(result, 10)

        # Decorators (with defaults) should behave as expected
        @Door
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

        door = Door(test_fxn)

        # Call the Door with erroneous types based on annotations.
        with self.assertRaises(ParameterError):
            result = door(x='6')

    def test_required_arguments(self):
        # This property is critical for the functioning of the Neighborhood
        # object, since it determines what areguments are passed and *how* they
        # are passed.
        @Door
        def test1(x, y=1):
            x += y
            return x
        @Door
        def test2(a, b, *, x):
            b += a * x
            x += a
            return b, a

        @Door
        def test3(key1='beta', key2='beeeeta'):
            return

        @Door
        def test4():
            pass

        @Door
        def test5():
            x = 5
            return x

        test_cases = (
                (test1, ['x']),
                (test2, ['a', 'b', 'x']),
                (test3, []),
                (test4, []),
                (test5, [])
                )

        for fxn, exp in test_cases:
            self.assertEqual(fxn.required_arguments, exp)

    def test_variables(self):
        @Door
        def test1(x, y=1):
            x += y
            return x
        @Door
        def test2(a, b, *, x):
            b += a * x
            x += a
            return b, a

        @Door
        def test3(key1='beta', key2='beeeeta'):
            return

        @Door
        def test4():
            pass

        @Door
        def test5():
            x = 5
            return x

        test_cases = (
                (test1, ['x', 'y']),
                (test2, ['a', 'b', 'x']),
                (test3, ['key1', 'key2']),
                (test4, []),
                (test5, ['x'])
                )

        for fxn, exp in test_cases:
            self.assertEqual(fxn.variables, exp)


if __name__ == "__main__":
    unittest.main()
