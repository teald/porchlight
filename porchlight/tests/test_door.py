"""Tests to verify the integrity of the porchlight.door.Door class and any
relevant helper functions or objects.
"""
from unittest import TestCase
import unittest

from porchlight.door import Door, DoorError
from porchlight.param import Empty, Param, ParameterError

import typing
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

        # Call the Door
        result = door(x=5)

        self.assertEqual(result, 10)

        # Decorators (with defaults) should behave as expected
        @Door
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

        door = Door(test_fxn)

        # Call the Door with erroneous types based on annotations.
        with self.assertRaises(ParameterError):
            door(x="6")

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
        def test3(key1="beta", key2="beeeeta"):
            return

        @Door
        def test4():
            pass

        @Door
        def test5():
            x = 5
            return x

        test_cases = (
            (test1, ["x"]),
            (test2, ["a", "b", "x"]),
            (test3, []),
            (test4, []),
            (test5, []),
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
        def test3(key1="beta", key2="beeeeta"):
            return

        @Door
        def test4():
            pass

        @Door
        def test5():
            x = 5
            return x

        test_cases = (
            (test1, ["x", "y"]),
            (test2, ["a", "b", "x"]),
            (test3, ["key1", "key2"]),
            (test4, []),
            (test5, ["x"]),
        )

        for fxn, exp in test_cases:
            self.assertEqual(fxn.variables, exp)

    def test___repr___(self):
        def test(x: int) -> int:
            y = x ** 2
            return y

        expected_repr = (
            f"Door(name=test, base_function={str(test)}, "
            f"arguments={{'x': <class 'int'>}}, "
            f"return_vals=[['y']])"
        )

        test_door = Door(test)
        self.assertEqual(repr(test_door), expected_repr)

    def test_mapping_args(self):
        @Door(argument_mapping={"hello": "x", "world": "y"})
        def my_func(x, y: int = 1):
            z = x + y
            x = x - 1
            return z, x

        @Door
        def orig_func(x, y: int = 1):
            z = x + y
            x = x - 1
            return z, x

        self.assertEqual(my_func.variables, ["hello", "world", "z"])
        self.assertEqual(my_func.return_vals, [["z", "hello"]])
        self.assertEqual(my_func.required_arguments, ["hello"])
        self.assertEqual(my_func.original_arguments, orig_func.arguments)
        self.assertEqual(my_func.original_return_vals, orig_func.return_vals)
        self.assertEqual(
            [x.value for x in my_func.keyword_args.values()],
            [x.value for x in orig_func.keyword_args.values()],
        )

        # Mapping with more significant changes
        @Door(argument_mapping={"pressure": "P", "temperature": "T"})
        def test2_mapped(
            T: float = 273.0, P: float = 1.01325e5, k_B: float = 1.38e-23
        ) -> float:
            density = P / (k_B * T)
            return density

        @Door
        def test2_unmapped(
            T: float = 273.0, P: float = 1.01325e5, k_B: float = 1.38e-23
        ) -> float:
            density = P / (k_B * T)
            return density

        self.assertEqual(
            test2_mapped.variables,
            ["temperature", "pressure", "k_B", "density"],
        )
        self.assertEqual(test2_mapped.return_vals, [["density"]])
        self.assertEqual(test2_mapped.required_arguments, [])
        self.assertEqual(
            test2_mapped.original_arguments, test2_unmapped.arguments
        )
        self.assertEqual(
            test2_mapped.original_return_vals, test2_unmapped.return_vals
        )
        self.assertEqual(
            [x.value for x in test2_mapped.keyword_args.values()],
            [x.value for x in test2_unmapped.keyword_args.values()],
        )

        # Empty mapping
        @Door(argument_mapping={})
        def test3():
            pass

        @Door(argument_mapping={})
        def test4(x):
            pass

        self.assertEqual(list(test4.arguments.keys()), ["x"])

    def test_mapping_multiple_returns(self):
        @Door(argument_mapping={"hello": "x", "bing": "z"})
        def test1(x, y: int, z=1) -> typing.Tuple[int]:
            result = True if x < y else False

            if result:
                return result, x, z

            else:
                return result, y, z

        self.maxDiff = None
        self.assertEqual(
            test1.return_vals,
            [["result", "hello", "bing"], ["result", "y", "bing"]],
        )
        self.assertEqual(list(test1.arguments.keys()), ["hello", "y", "bing"])
        self.assertEqual(
            test1.keyword_arguments,
            {
                "hello": Param("hello"),
                "y": Param("y"),
                "bing": Param("bing", 1),
            },
        )

    def test_bad_mapping_variable_names(self):
        bad_names = ("0fign_", " bonk", "this is a sentence...", "there.dot")
        good_names = ("_wello", "Im_fiNe_in_A_WAy", "_____", "h0rch4t4")

        @Door
        def base_def(x):
            pass

        for name in bad_names:
            with self.assertRaises(DoorError):
                cur_map = {name: "x"}
                Door(argument_mapping=cur_map)(base_def)

        for name in good_names:
            cur_map = {name: "x"}
            Door(argument_mapping=cur_map)(base_def)

    def test_nested_mapping(self):
        @Door(argument_mapping={"hello": "x", "world": "z"})
        def test1(x, y: int, z=1) -> int:
            total = x + y * z
            return total

        test2 = Door(test1)

        self.assertEqual(test2.arguments, {"x": Empty, "y": int, "z": Empty})

    def test_bad_mapping_bad_functions(self):
        # A bad argument
        with self.assertRaises(DoorError):

            @Door(argument_mapping={"not": "here"})
            def test1():
                pass

    def test_bad_mapping_uninitialized(self):
        with self.assertRaises(DoorError):
            my_door = Door(argument_mapping={})
            my_door.map_arguments()

    def test_bad_call_inputs(self):
        with self.assertRaises(TypeError):
            Door(argument_mapping={})(1)

        with self.assertRaises(ValueError):

            def test1():
                pass

            Door(argument_mapping={})(test1, 1, y=2)

    def test_bad_mapping_name_err_and_warning(self):
        with self.assertRaises(DoorError):

            @Door(argument_mapping={"x": "y"})
            def test1(x, y):
                pass

    def test_argument_mapping_property(self):
        @Door(argument_mapping={"hello": "x", "world": "z"})
        def test1(x, y: int, z=1) -> int:
            total = x + y * z
            return total

        self.assertEqual(test1.argument_mapping, {"hello": "x", "world": "z"})

        # Changing the argument mapping with the setter.
        test1.argument_mapping = {"hello_again": "x", "world_two": "z"}


if __name__ == "__main__":
    unittest.main()
