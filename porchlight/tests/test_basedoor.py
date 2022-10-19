"""Tests to verify the integrity of the porchlight.door.BaseDoor class and any
relevant helper functions or objects.
"""
from unittest import TestCase

import porchlight.door as door
from porchlight.door import BaseDoor
from porchlight.param import Empty, ParameterError, Param

import logging
import os

logging.basicConfig(filename=f"{os.getcwd()}/porchlight_unittest.log")


class TestBaseDoor(TestCase):
    def test___init__(self):
        def test_fxn(x: int) -> int:
            y = 2 * x
            return y

        door = BaseDoor(test_fxn)

        # Must contain both input and output parameter.
        arguments = ["x"]
        keyword_args = ["x"]
        return_vals = [["y"]]

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

        self.assertEqual(fxn_use_decorator.name, "fxn_use_decorator")

        self.assertEqual(fxn_use_decorator.arguments, {"x": Empty})

    def test___call__(self):
        def test_fxn(x: int) -> int:
            y = 2 * x
            return y

        door = BaseDoor(test_fxn)

        # Call the BaseDoor with erroneous types based on annotations.
        with self.assertRaises(ParameterError):
            door(x="6")

    def test__get_return_vals(self):
        # Should be able to handle one return val.
        def fxn_one_return(x):
            y = 1
            return y

        result = BaseDoor._get_return_vals(fxn_one_return)

        self.assertEqual(result, [["y"]])

        # Multiple return values, no inputs
        def fxn_no_inputs():
            x, y, z, = (
                0,
                0,
                0,
            )
            return x, y, z

        result = BaseDoor._get_return_vals(fxn_no_inputs)

        self.assertEqual([["x", "y", "z"]], result)

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

        self.assertEqual([["outstr"]], result)

        # Test retrieving a return value for a function that wraps another
        # function to return.
        def test_wrap():
            def int_func():
                output = "Hello world!"
                return output

            return int_func

        result = BaseDoor._get_return_vals(test_wrap)

        self.assertEqual(result, [["int_func"]])

        # Test single-line definitions.
        def test_oneline(x):
            return x

        result = BaseDoor._get_return_vals(test_oneline)

        self.assertEqual(result, [["x"]])

        def test_oneline_bad(x):
            return x * 2

        result = BaseDoor._get_return_vals(test_oneline_bad)

        self.assertEqual(result, [])

        # Tests with non-return values in it.
        class Return_Type:
            pass

        def bad_ret_vals() -> Return_Type:
            return_at_beginning = None
            mid_return_loc = None
            end_loc_return = None

            # To appease flake8
            other_ret = (return_at_beginning, mid_return_loc, end_loc_return)

            other_ret = Return_Type()
            return other_ret

        result = BaseDoor._get_return_vals(bad_ret_vals)

        self.assertEqual(result, [["other_ret"]])

    def test___eq__(self):
        @BaseDoor
        def fxn1(x, y):
            x += y

            return x

        @BaseDoor
        def fxn2(x, y):
            return y

        other_fxn1 = door.BaseDoor(fxn1._base_function)

        self.assertTrue(fxn1 == fxn1)
        self.assertFalse(fxn1 == fxn2)
        self.assertTrue(fxn1 == other_fxn1)

    def test__inspect_base_callable(self):
        def bigfxn(x, y, *, z=5):
            output = sum((x, y, z))
            return output

        new_door = BaseDoor(bigfxn)

        self.assertEqual(new_door.keyword_only_args, {"z": Param("z", 5)})

        # For now, there should *not* be any functionality for required
        # positional arguments. That will come later, and this test will need
        # to be updated.
        def bad_fxn(x1, y1, /, x3, *, z7):
            c = "blah"
            return c

        with self.assertRaises(NotImplementedError):
            BaseDoor(bad_fxn)


if __name__ == "__main__":
    import unittest

    unittest.main()
