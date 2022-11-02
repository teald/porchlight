"""Tests for the porchlight.door.DynamicDoor class."""
import porchlight.door as door

import unittest

import os


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


if __name__ == "__main__":
    unittest.main()
