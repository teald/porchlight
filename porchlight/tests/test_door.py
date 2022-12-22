"""Tests to verify the integrity of the porchlight.door.Door class and any
relevant helper functions or objects.
"""
from unittest import TestCase
import unittest

from porchlight.door import Door, DoorError, DoorWarning
from porchlight.param import Empty, Param, ParameterError

import typing
import logging
import os
import math
import random

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
        return_vals = ["y"]

        # Not comparing any values during this test.
        for arg in arguments:
            self.assertIn(arg, door.arguments)

        for kwarg in keyword_args:
            self.assertIn(kwarg, door.keyword_args)

        self.assertEqual(return_vals, door.return_vals)

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

        self.assertEqual(fxn_use_decorator.arguments, {"x": Empty()})

        # Try manually naming the door.
        @Door(name="testname")
        def test1():
            pass

        self.assertEqual(test1.__name__, "testname")
        self.assertEqual(test1.name, "testname")

    def test___call__(self):
        def test_fxn(x: int) -> int:
            y = 2 * x
            return y

        door = Door(test_fxn, typecheck=True)

        # Call the Door with erroneous types based on annotations.
        with self.assertRaises(ParameterError):
            door(x="6")

        # Typechecking off
        door = Door(test_fxn, typecheck=False)
        door(x="6")

        # Default functionality should be typechecking off
        door = Door(test_fxn)
        door(x=[6])

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
            f"return_vals=['y'])"
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
        self.assertEqual(my_func.return_vals, ["z", "hello"])
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
        self.assertEqual(test2_mapped.return_vals, ["density"])
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
        with self.assertRaises(DoorError):

            @Door(argument_mapping={"hello": "x", "bing": "z"})
            def test1(x, y: int, z=1) -> typing.Tuple[int]:
                result = True if x < y else False

                if result:
                    return result, x, z

                else:
                    return result, y, z

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

        self.assertEqual(
            test2.arguments, {"x": Empty(), "y": int, "z": Empty()}
        )

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

    def test_builtin_mapping_name_warning(self):
        with self.assertWarns(DoorWarning):

            @Door(argument_mapping={"type": "x"})
            def test1(x):
                pass

        with self.assertWarns(DoorWarning):

            @Door(argument_mapping={"hola": "type"})
            def test2(type):
                return

    def test_argument_mapping_property(self):
        @Door(argument_mapping={"hello": "x", "world": "z"})
        def test1(x, y: int, z=1) -> int:
            total = x + y * z
            return total

        self.assertEqual(test1.argument_mapping, {"hello": "x", "world": "z"})

        # Changing the argument mapping with the setter.
        test1.argument_mapping = {"hello_again": "x", "world_two": "z"}

    def test_argument_mapping_return_values(self):
        # Below works as expected. The return value is visible as 'why'.
        @Door(argument_mapping={"ecks": "x", "why": "y"})
        def test1(x, y):
            y = x + 1
            return y

        # This raises a DoorError
        @Door(argument_mapping={"ecks": "x", "why": "y"})
        def test2(x):
            y = x + 1
            return y

        # These tests should work exactly the same in terms of input/output.
        def testval():
            return random.randint(-10, 10)

        tests = [[testval(), testval()] for _ in range(100)]

        for x, y in tests:
            self.assertEqual(test1(x, y), test2(x))

    def test_auto_wrapping(self):
        # Should work for any type of callable.
        def my_func(x: int) -> int:
            y = x + 1
            return y

        tests = [
            (
                my_func,
                {"arguments": {"hello": int}, "return_vals": ["world"]},
            ),
            (
                lambda x: x + 1,
                {"arguments": {"x": int}, "return_vals": ["y"]},
            ),
            (
                math.cos,
                {
                    "arguments": {"theta": int},
                    "return_vals": ["cos_theta"],
                },
            ),
        ]

        for fxn, kwargs in tests:
            my_door = Door(fxn, wrapped=True, **kwargs)

            for arg, value in kwargs.items():
                self.assertEqual(getattr(my_door, arg), value)

        # Actually run the Door
        my_door = Door(my_func, wrapped=True, **tests[0][1])
        expected_output = [my_func(x) for x in range(10)]
        output = [my_door(x) for x in range(10)]

        self.assertEqual(expected_output, output)

        # Test a slightly more complicated door.
        def test1(x: int, *, y=0) -> int:
            z = x ** y
            return z

        kwargs = {
            "arguments": {"x": int},
            "keyword_args": {"y": 0},
            "return_vals": ["z"],
        }

        normal_door = Door(test1)
        wrapped_door = Door(test1, wrapped=True, **kwargs)

        self.assertEqual(normal_door(5), wrapped_door(5))
        self.assertEqual(normal_door(-500, y=2), wrapped_door(-500, y=2))

        # Auto-wrapping cannot be used with decorators.
        with self.assertRaises(DoorError):

            @Door(wrapped=True, **kwargs)
            def test2(x: int, *, y=0) -> int:
                z = x ** y
                return z


if __name__ == "__main__":
    unittest.main()
