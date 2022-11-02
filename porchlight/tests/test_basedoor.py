"""Tests to verify the integrity of the porchlight.door.BaseDoor class and any
relevant helper functions or objects.
"""
from unittest import TestCase

import porchlight.door as door
from porchlight.door import BaseDoor
from porchlight.param import Empty, ParameterError, Param

import logging
import os

from typing import Callable

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

        # Tests with non-return local variables.
        class Return_Type:
            pass

        def bad_ret_vals() -> Return_Type:
            return_at_beginning = None
            mid_return_loc = None
            end_loc_return = None

            # To appease flake8, but also a test itself.
            other_ret = (return_at_beginning, mid_return_loc, end_loc_return)
            other_ret = "Putting return in a new place: return"

            other_ret = Return_Type()
            return other_ret

        result = BaseDoor._get_return_vals(bad_ret_vals)

        self.assertEqual(result, [["other_ret"]])

        # TODO: Below is commented out intentionally for github issue #17.
        # # Test decorators.
        # def dummy_decorator(fun) -> Callable:
        #     def wrapper(*args, **kwargs):
        #         return fun(*args, **kwargs)

        #     return wrapper

        # @dummy_decorator
        # def test_decorator() -> int:
        #     x = 1
        #     return x

        # result = BaseDoor._get_return_vals(test_decorator)

        # self.assertEqual(result, [["x"]])

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

    def test___repr__(self):
        """Test the BaseDoor"""

        def test(x: int) -> int:
            y = x ** 2
            return y

        expected_repr = (
            f"BaseDoor(name=test, base_function={str(test)}, "
            f"arguments={{'x': <class 'int'>}}, "
            f"return_vals=[['y']])"
        )

        test_door = BaseDoor(test)
        self.assertEqual(repr(test_door), expected_repr)

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

    def test__returned_def_to_door(self):
        def my_func_gen():
            def int_func():
                output = "bingbong"
                return output

            return int_func

        no_int_ret_door = BaseDoor(my_func_gen)
        int_ret_door = BaseDoor(my_func_gen, returned_def_to_door=True)

        self.assertEqual(no_int_ret_door.name, int_ret_door.name)
        self.assertEqual(no_int_ret_door.arguments, int_ret_door.arguments)

        self.assertTrue(isinstance(no_int_ret_door(), Callable))
        self.assertTrue(isinstance(int_ret_door(), BaseDoor))

    def test_keyword_arguments(self):
        @BaseDoor
        def test_prop(arg1, arg2, kwarg1=None, kwarg2=["hi"]) -> int:
            kwarg1 = 1 if kwarg1 is None else kwarg1 + 1
            return kwarg1

        expected_val = {
            "arg1": Param("arg1", Empty()),
            "arg2": Param("arg2", Empty()),
            "kwarg1": Param("kwarg1", None),
            "kwarg2": Param("kwarg2", ["hi"]),
        }
        self.assertEqual(test_prop.keyword_arguments, expected_val)

    def test_kwargs(self):
        @BaseDoor
        def test_prop(arg1, arg2, kwarg1=None, kwarg2=["hi"]) -> int:
            kwarg1 = 1 if kwarg1 is None else kwarg1 + 1
            return kwarg1

        expected_val = {
            "arg1": Param("arg1", Empty()),
            "arg2": Param("arg2", Empty()),
            "kwarg1": Param("kwarg1", None),
            "kwarg2": Param("kwarg2", ["hi"]),
        }
        self.assertEqual(test_prop.kwargs, expected_val)


if __name__ == "__main__":
    import unittest

    unittest.main()
