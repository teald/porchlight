import porchlight
from porchlight import Neighborhood, Door, Param, door

import unittest
from unittest import TestCase

import logging
import os
import typing

logging.basicConfig(filename=f"{os.getcwd()}/porchlight_unittest.log")


class TestNeighborhood(TestCase):
    def test___init___(self):
        # Plain initialization should not do anything beyond defining the empty
        # Neighborhood._doors and Neighborhood._params attrs
        neighborhood = Neighborhood()

        self.assertEqual(neighborhood._doors, {})
        self.assertEqual(neighborhood._params, {})

    def test___init___with_list(self):
        def test1(x):
            pass

        @door.Door
        def test2(y: int) -> int:
            z = y + 10
            return z

        neighborhood = Neighborhood([test1, test2])

        self.assertEqual(list(neighborhood.params.keys()), ['x', 'y', 'z'])

    def test___repr__(self):
        neighborhood = Neighborhood()
        expected = r"Neighborhood(doors={}, params={}, call_order=[])"
        self.assertEqual(repr(neighborhood), expected)

        @Door
        def test1(x: int) -> int:
            y = x + 1
            return y

        neighborhood.add_door(test1)

        # Keeping the below as an example of what the string looks like. Update
        # this to match the actual implementation as changes occur below.
        # expected = (
        #     "Neighborhood(doors={'test1': Door(name=test1, "
        #     "base_function=<function test1 at 0x7f247d8c48b0>, "
        #     "arguments={'x': <class 'int'>}, return_vals=[['y']])}, "
        #     "params={'x': Param(name=x, value=<porchlight.param."
        #     "Empty object at 0x7f247e1bd060>, constant=False, type=<class "
        #     "'porchlight.param.Empty'>), 'y': Param(name="
        #     "y, value=<porchlight.param.Empty object at 0x7f247d8c9660>, "
        #     "constant=False, type=<class 'porchlight.param "
        #     ".Empty'>)}, call_order=['test1'])"
        # )

        params = neighborhood.params

        expected = (
            f"Neighborhood(doors={{'test1': {test1}}}, "
            f"params={params}, call_order=['test1'])"
        )

        print(repr(neighborhood))
        self.assertEqual(repr(neighborhood), expected)

    def test_add_function(self):
        # We only need to test if the correct type of door is created---can
        # compare them directly.
        neighborhood = Neighborhood()

        def test1(x, y=1) -> int:
            z = x + y
            return z

        door_equiv = Door(test1)

        neighborhood.add_function(test1)

        self.assertTrue(len(neighborhood._doors) == 1)
        self.assertTrue(len(neighborhood._params) == 3)

        neighborhood_door = list(neighborhood._doors.values())[0]
        self.assertTrue(neighborhood_door == door_equiv)

        # Now try to overwrite the function.
        def test1(x, y=2) -> int:
            z = x + y
            return z

        neighborhood.add_function(test1)

        self.assertEqual(neighborhood._params["y"].value, 1)

        # Now actually overwrite the function.
        neighborhood.add_function(test1, overwrite_defaults=True)

        self.assertEqual(neighborhood._params["y"].value, 2)

    def test_add_door(self):
        # We only need to test if the correct type of door is created---can
        # compare them directly.
        neighborhood = Neighborhood()

        @Door
        def test1(x, y=1) -> int:
            z = x + y
            return z

        neighborhood.add_door(test1)

        self.assertTrue(len(neighborhood._doors) == 1)
        self.assertTrue(len(neighborhood._params) == 3)

        # Now try to overwrite the function.
        @Door
        def test1(x, y=2) -> int:
            z = x + y
            return z

        neighborhood.add_door(test1)

        self.assertEqual(neighborhood._params["y"].value, 1)

        # Now actually overwrite the function.
        neighborhood.add_door(test1, overwrite_defaults=True)

        self.assertEqual(neighborhood._params["y"].value, 2)

        # Add a different Door
        @Door
        def test2(x, z):
            y = x + z
            return y

        neighborhood.add_door(test2)

        self.assertEqual(len(neighborhood._doors), 2)

        # Since Neighborhood.remove_door has only one use case, cover that
        # here.
        neighborhood.remove_door(test2.name)

        self.assertEqual(len(neighborhood._doors), 1)

        neighborhood.remove_door("test1")

        self.assertEqual(len(neighborhood._doors), 0)

        # Testing adding multiple doors as once.
        @Door
        def test1(x, y=1) -> int:
            z = x + y
            return z

        @Door
        def test2(z):
            z = 3 * z
            return z

        @Door
        def test3():
            pass

        @Door
        def test4():
            arbitrary = None
            return arbitrary

        neighborhood = Neighborhood()

        neighborhood.add_door([test1, test2, test3, test4])

        self.assertEqual(len(neighborhood._doors), 4)
        self.assertEqual(len(neighborhood._params), 4)

        # Empty, unused variable test.
        @Door
        def test1(x):
            y = 10 + x
            return y

        @Door
        def test2(x):
            z = 5 + x
            return z

        @Door
        def test3():
            pass

        @Door
        def test4():
            return

        # Mix and match different adding formats.
        neighborhood.add_door(test1)
        neighborhood.add_door(test2)
        neighborhood.add_door([test3, test4])

    @unittest.skip(
        "Already comprehensively tested by other tests for the "
        "time being, but will need to be intdependently tested "
        "once Groups are implemented"
    )
    def test_add_param(self):
        pass

    def test_run_step(self):
        @Door
        def test1(x, y=1) -> int:
            z = x + y
            return z

        @Door
        def test2(z):
            z = 3 * z
            return z

        @Door
        def test3():
            pass

        @Door
        def test4():
            arbitrary = None
            something_else = 5
            return arbitrary, something_else

        neighborhood = Neighborhood()

        neighborhood.add_door([test1, test2, test3, test4])

        neighborhood.add_param("x", 1)
        neighborhood.add_param("z", 1)

        neighborhood.run_step()
        neighborhood.run_step()
        neighborhood.run_step()

        # Check that the state of the parameters is the expected values
        x = neighborhood._params["x"]
        y = neighborhood._params["y"]
        z = neighborhood._params["z"]
        arb = neighborhood._params["arbitrary"]
        smthn = neighborhood._params["something_else"]

        self.assertEqual(x._value, 1)
        self.assertEqual(y._value, 1)
        self.assertEqual(z._value, 6)
        self.assertEqual(smthn._value, 5)
        self.assertTrue(arb._value is None)

        # Test updating a new, empty parameter that will be updated by a return
        # value.
        def retval_empty_test(x):
            rettest = x + 1
            return rettest

        neighborhood.add_function(retval_empty_test)

        self.assertEqual(
            neighborhood._params["rettest"].value, porchlight.param.Empty()
        )

        neighborhood.run_step()

        expected_param = porchlight.param.Param(
            "rettest", neighborhood.params["x"].value + 1
        )

        self.assertEqual(
            neighborhood._params["rettest"].value, expected_param.value
        )

        # Make one of the parameters constant.
        neighborhood.set_param("rettest", 1, constant=True)

        with self.assertRaises(porchlight.param.ParameterError):
            neighborhood.run_step()

    def test_empty_variable_check(self):
        # Empty, unused variable test.
        @Door
        def test1(x):
            y = 10 + x
            return y

        @Door
        def test2(x):
            z = 5 + x
            return z

        @Door
        def test3():
            pass

        @Door
        def test4():
            return

        neighborhood = Neighborhood()
        neighborhood.add_door(test1)
        neighborhood.add_door(test2)
        neighborhood.add_door([test3, test4])

        # Don't pass the required parameters
        with self.assertRaises(porchlight.param.ParameterError):
            neighborhood.run_step()

    def test_order_doors(self):
        neighborhood = Neighborhood()

        @Door
        def test1(x, y, z=1):
            x += y + z
            return x

        @Door
        def test2(z):
            z *= 5
            return z

        @Door
        def test3():
            pass

        @Door
        def test4(x):
            outstr = str(f"My x is: {x}")
            return outstr

        neighborhood.add_door([test1, test2, test3, test4])

        self.assertEqual(
            neighborhood._call_order, ["test1", "test2", "test3", "test4"]
        )

        neighborhood.order_doors(["test2", "test1", "test4", "test3"])

        self.assertEqual(
            neighborhood._call_order, ["test2", "test1", "test4", "test3"]
        )

        # Should raise an error if a door is missing/extra door provided.
        with self.assertRaises(ValueError):
            neighborhood.order_doors(["t", "t", "t", "t", "test4"])

        with self.assertRaises(ValueError):
            neighborhood.order_doors([])

        with self.assertRaises(KeyError):
            neighborhood.order_doors([""])

        with self.assertRaises(KeyError):
            # test2 -> tset2
            neighborhood.order_doors(["test1", "tset2", "test3", "test4"])

    def test_remove_door(self):
        @Door
        def test1(x, y, z=1):
            x += y + z
            return x

        @Door
        def test2(z):
            z *= 5
            return z

        @Door
        def test3():
            pass

        @Door
        def test4(x):
            outstr = str(f"My x is: {x}")
            return outstr

        neighborhood = Neighborhood()
        neighborhood.add_door([test1, test2, test3, test4])

        neighborhood.remove_door("test1")

        self.assertEqual(len(neighborhood.doors), 3)
        self.assertEqual(
            neighborhood._doors,
            {"test2": test2, "test3": test3, "test4": test4},
        )

        with self.assertRaises(KeyError):
            neighborhood.remove_door("bad door")

        # Make sure that the remove door has stayed removed, and that it's no
        # longer referenced in the Neighborhood._doors attr
        with self.assertRaises(KeyError):
            neighborhood.remove_door("test1")

    def test_required_args_present(self):
        @Door
        def test1(x, y=2, *, z):
            return x

        neighborhood = Neighborhood()

        neighborhood.add_door(test1)

        self.assertFalse(neighborhood.required_args_present())

        neighborhood.set_param("x", 7)
        neighborhood.set_param("z", "fourty-two")

        def test2(x, z):
            y = x + z
            return y

        neighborhood.add_function(test2)

        self.assertTrue(neighborhood.required_args_present())

    def test_set_param(self):
        @Door
        def test1(x):
            return

        neighborhood = Neighborhood()

        neighborhood.add_door(test1)

        self.assertEqual(
            neighborhood._params["x"].value, porchlight.param.Empty()
        )

        neighborhood.set_param("x", 1)

        self.assertEqual(neighborhood._params["x"].value, 1)

        # Test constants
        @Door
        def test2(y):
            out = str(y)
            return out

        neighborhood.add_door(test2)

        neighborhood.add_param("y", 1, constant=True)

        with self.assertRaises(porchlight.param.ParameterError):
            neighborhood.set_param("y", 5)

        neighborhood.set_param("y", 5, ignore_constant=True)

        expected_param = porchlight.param.Param("y", 5)
        self.assertEqual(neighborhood._params["y"], expected_param)

    def test_anticipated_parameters(self):
        def fxn_one(x):
            y = x + 1
            return y

        def fxn_two(y):
            return "Hello!"

        neighborhood = Neighborhood()

        neighborhood.add_function(fxn_one)
        neighborhood.add_function(fxn_two)

        # Provide the required first arg, x
        neighborhood.set_param("x", 0)

        neighborhood.run_step()

        # Check that y is now sucessfully initialized.
        expected_param = Param("y", 1)
        self.assertEqual(neighborhood._params["y"], expected_param)

        # Make sure the value doesn't change after another run.
        neighborhood.run_step()
        self.assertEqual(neighborhood._params["y"], expected_param)

        # If another uninitialized value is added but will not be created, the
        # neighborhood should raise an error.
        @Door
        def fxn_three(barf):
            return

        neighborhood.add_door(fxn_three)

        with self.assertRaises(porchlight.param.ParameterError):
            neighborhood.run_step()

    def test_uninitialized_inputs(self):
        @Door
        def test1(x, y=1):
            z = x * y
            return z

        @Door
        def test2(z):
            return

        @Door
        def test3():
            x = 0
            return x

        neighborhood = Neighborhood()

        neighborhood.add_door([test1, test2, test3])

        self.assertEqual(neighborhood.uninitialized_inputs, ["x", "z"])

    def test_dynamic_doors(self):
        # TODO: There is a case for updating multiple doors with one function.
        # It shouldn't be too hard to execute, but need to keep it in mind.
        @Door
        def test1(x: int) -> Door:
            @Door
            def test1_door():
                y = x + 1
                return y

            return test1_door

        neighborhood = Neighborhood()

        # Adding this to the neighborhood should add two doors.
        neighborhood.add_door(test1, dynamic_door=True)

        self.assertEqual(
            list(neighborhood.doors.keys()), ["test1", "test1_door"]
        )

        self.assertEqual(list(neighborhood.params.keys()), ["x", "test1_door"])

        neighborhood.set_param("x", 1)
        neighborhood.run_step()

        self.assertEqual(neighborhood.params["y"].value, 2)

        # Now add a dynamic door with a keyword argument.
        @Door
        def test2() -> Door:
            @Door
            def test2_door(z: int = 3):
                # Note: this will override any previously calculated values of
                # y---on purpose here!
                y = z + 3
                return y

            return test2_door

        neighborhood.add_door(test2, dynamic_door=True)
        neighborhood.run_step()

        self.assertEqual(
            list(neighborhood.doors.keys()),
            ["test1", "test1_door", "test2", "test2_door"],
        )
        self.assertEqual(neighborhood.params["y"].value, 6)
        self.assertEqual(
            list(neighborhood.params.keys()),
            ["x", "test1_door", "y", "test2_door", "z"],
        )

        # This should fail if dynamic doors are not requested.
        neighborhood = Neighborhood()
        neighborhood.add_door(test1)

        self.assertEqual(list(neighborhood.doors.keys()), ["test1"])

        self.assertEqual(list(neighborhood.params.keys()), ["x", "test1_door"])

        # Add two dynamic doors using a single generator function.
        def doublegen_test(
            x: float,
        ) -> typing.Tuple[porchlight.Door, porchlight.Door]:
            @porchlight.Door
            def test1(y: float) -> float:
                z = y ** x + 1
                return z

            @porchlight.Door
            def test2(z: float) -> float:
                x = 2 * z
                return x

            return test1, test2

        neighborhood = Neighborhood()
        neighborhood.add_function(doublegen_test, dynamic_door=True)
        neighborhood.add_param("x", 0.0)
        neighborhood.add_param("y", 2.0)

        expected_doors = ["doublegen_test", "test1", "test2"]
        expected_params = ["x", "test1", "test2", "y", "z"]

        self.assertEqual(list(neighborhood.doors.keys()), expected_doors)

        neighborhood.run_step()

        self.assertEqual(list(neighborhood.params.keys()), expected_params)
        self.assertAlmostEqual(neighborhood.params["x"].value, 4.0)
        self.assertAlmostEqual(neighborhood.params["y"].value, 2.0)
        self.assertAlmostEqual(neighborhood.params["z"].value, 2.0)

        neighborhood.run_step()

        self.assertEqual(list(neighborhood.params.keys()), expected_params)
        self.assertAlmostEqual(neighborhood.params["x"].value, 34.0)
        self.assertAlmostEqual(neighborhood.params["y"].value, 2.0)
        self.assertAlmostEqual(neighborhood.params["z"].value, 17.0)

    def test_bad_dynamic_door(self):
        @Door
        def test1(x: int):
            @Door
            def test1_door():
                y = x + 1
                return y

            return test1_door

        neighborhood = Neighborhood()

        # Adding this to the neighborhood should add two doors.
        with self.assertRaises(porchlight.neighborhood.NeighborhoodError):
            neighborhood.add_door(test1, dynamic_door=True)

    def test_properties(self):
        @porchlight.Door
        def test1(x: typing.Union[int, float], y: str = "15.5") -> typing.Any:
            z = x + float(y)
            return z

        neighborhood = Neighborhood()
        neighborhood.add_door(test1)

        # Neighborhood.parameters
        result = neighborhood.parameters
        self.assertEqual(result["x"], Param("x", porchlight.param.Empty()))
        self.assertEqual(result["y"], Param("y", "15.5"))

    def test_bad_dynamicdoor_return_values(self):
        @porchlight.door.DynamicDoor
        def test1():
            def bad():
                x = 1
                return x

            return bad

        neighborhood = Neighborhood()

        with self.assertRaises(porchlight.neighborhood.NeighborhoodError):
            neighborhood.add_door(test1, dynamic_door=True)

    def test_get_value(self):
        def test1(x, y=1):
            z = x + y
            return z

        neighborhood = Neighborhood()

        neighborhood.add_function(test1)
        neighborhood.set_param("x", 1)
        neighborhood.run_step()

        expected = {
            "x": 1,
            "y": 1,
            "z": 2,
        }

        for pname, val in expected.items():
            self.assertEqual(val, neighborhood.get_value(pname))


if __name__ == "__main__":
    import unittest

    unittest.main()
