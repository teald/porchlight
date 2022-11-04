"""Tests for the porchlight.door.DynamicDoor class."""
import porchlight.door as door

import os
import unittest


class TestDynamicDoor(unittest.TestCase):
    def test___init__(self):
        @door.DynamicDoor
        def doorgen1() -> door.Door:
            @door.Door
            def my_door(x: int) -> int:
                y = x + 1
                return y

            return my_door

        self.assertEqual(doorgen1._door_generator.__name__, "doorgen1")
        self.assertEqual(doorgen1.generator_args, [])
        self.assertEqual(doorgen1.generator_kwargs, {})

        doorgen1.update()

        self.assertEqual(doorgen1.name, "my_door")
        self.assertEqual(doorgen1.variables, ["x", "y"])

        _y = doorgen1(3)

        self.assertEqual(_y, 4)

    def test___repr__(self):
        @door.DynamicDoor
        def doorgen1() -> door.Door:
            @door.Door
            def my_door(x: int) -> int:
                y = x + 1
                return y

            return my_door

        # Initially, should be uninitialized with no meta-info.
        self.assertEqual(repr(doorgen1), "DynamicDoor(uninitialized)")

        # Once the generator function has been run once and the Dynamic door
        # has been updated, expect a door-like string with "Dynamic" prepended.
        doorgen1(1)
        my_door = doorgen1._cur_door
        expected_repr = repr(my_door)
        expected_repr = expected_repr.replace("Door", "DynamicDoor")

        self.assertEqual(repr(doorgen1), expected_repr)

    def test_bad_returns(self):
        # Non-BaseDoor returns should raise a TypeError at update.
        def test1() -> int:
            return 1

        def test2() -> str:
            x = ""
            return x

        def test3(x: int) -> int:
            return x

        def test4() -> door.Door:
            return

        def test5() -> door.BaseDoor:
            x = 1
            return x

        def test6(bing: str) -> door.Door:
            def fxn():
                return "hello"

            return fxn

        all_tests = [test1, test2, test3, test4, test5, test6]

        for test in all_tests:
            with self.assertRaises(TypeError):
                new_ddoor = door.DynamicDoor(test)
                new_ddoor.update()


if __name__ == "__main__":
    unittest.main()
