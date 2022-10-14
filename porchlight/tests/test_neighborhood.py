import neighborhood
from neighborhood import Neighborhood

from door import Door
import param
from param import ParameterError, Empty

import unittest
from unittest import TestCase

import logging
import os
logging.basicConfig(filename=f"{os.getcwd()}/porchlight_unittest.log")


class TestNeighborhood(TestCase):
    def test___init___(self):
        # Initialization should not do anything beyond defining the empty
        # Neighborhood._doors and Neighborhood._params attrs
        neighborhood = Neighborhood()

        self.assertEqual(neighborhood._doors, {})
        self.assertEqual(neighborhood._params, {})

    def test_add_function(self):
        # We only need to test if the correct type of door is created---can
        # compare them directly.
        neighborhood = Neighborhood()

        def test1(x, y = 1) -> int:
            z = x + y
            return z

        door_equiv = Door(test1)

        neighborhood.add_function(test1)

        self.assertTrue(len(neighborhood._doors) == 1)
        self.assertTrue(len(neighborhood._params) == 3)

        neighborhood_door = list(neighborhood._doors.values())[0]
        self.assertTrue(neighborhood_door == door_equiv)

        # Now try to overwrite the function.
        def test1(x, y = 2) -> int:
            z = x + y
            return z

        neighborhood.add_function(test1)

        self.assertEqual(neighborhood._params['y'].value, 1)

        # Now actually overwrite the function.
        neighborhood.add_function(test1, overwrite_defaults=True)

        self.assertEqual(neighborhood._params['y'].value, 2)

    def test_add_door(self):
        # We only need to test if the correct type of door is created---can
        # compare them directly.
        neighborhood = Neighborhood()

        @Door
        def test1(x, y = 1) -> int:
            z = x + y
            return z

        neighborhood.add_door(test1)

        self.assertTrue(len(neighborhood._doors) == 1)
        self.assertTrue(len(neighborhood._params) == 3)

        # Now try to overwrite the function.
        @Door
        def test1(x, y = 2) -> int:
            z = x + y
            return z

        neighborhood.add_door(test1)

        self.assertEqual(neighborhood._params['y'].value, 1)

        # Now actually overwrite the function.
        neighborhood.add_door(test1, overwrite_defaults=True)

        self.assertEqual(neighborhood._params['y'].value, 2)

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
            return arbitrary

        neighborhood = Neighborhood()

        neighborhood.add_door(
                [test1, test2, test3, test4]
                )

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

    @unittest.skip("Already comprehensively tested by other tests for the "
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

        neighborhood.add_door(
                [test1, test2, test3, test4]
                )

        neighborhood.add_param('x', 1)
        neighborhood.add_param('z', 1)

        neighborhood.run_step()
        neighborhood.run_step()
        neighborhood.run_step()

        # Check that the state of the parameters is the expected values
        x = neighborhood._params['x']
        y = neighborhood._params['y']
        z = neighborhood._params['z']
        arb = neighborhood._params['arbitrary']
        smthn = neighborhood._params['something_else']

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

        self.assertEqual(neighborhood._params['rettest'].value, param.Empty())

        neighborhood.run_step()

        expected_param = param.Param('rettest',
                                     neighborhood.params['x'].value + 1
                                     )

        self.assertEqual(neighborhood._params['rettest'].value, expected_param.value)

        # Make one of the parameters constant.
        neighborhood.set_param('rettest', 1, constant=True)

        with self.assertRaises(param.ParameterError):
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
        with self.assertRaises(ParameterError):
            neighborhood.run_step()

    def test_remove_door(self):
        @Door
        def test1(x, y, z = 1):
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

        neighborhood.remove_door('test1')

        self.assertEqual(len(neighborhood.doors), 3)
        self.assertEqual(
                neighborhood._doors,
                {
                    'test2': test2,
                    'test3': test3,
                    'test4': test4
                    }
                )

        with self.assertRaises(KeyError):
            neighborhood.remove_door('bad door')

        # Make sure that the remove door has stayed removed, and that it's no
        # longer referenced in the Neighborhood._doors attr
        with self.assertRaises(KeyError):
            neighborhood.remove_door('test1')

    def test_required_args_present(self):
        @Door
        def test1(x, y = 2, *, z):
            return x

        neighborhood = Neighborhood()

        neighborhood.add_door(test1)

        self.assertFalse(neighborhood.required_args_present())

        neighborhood.set_param('x', 7)
        neighborhood.set_param('z', 'fourty-two')

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

        self.assertEqual(neighborhood._params['x'].value, Empty())

        neighborhood.set_param('x', 1)

        self.assertEqual(neighborhood._params['x'].value, 1)

        # Test constants
        @Door
        def test2(y):
            out = str(y)
            return out

        neighborhood.add_door(test2)

        neighborhood.add_param('y', 1, constant=True)

        with self.assertRaises(param.ParameterError):
            neighborhood.set_param('y', 5)

        neighborhood.set_param('y', 5, ignore_constant=True)

        expected_param = param.Param('y', 5)
        self.assertEqual(neighborhood._params['y'], expected_param)

if __name__ == "__main__":
    unittest.main()
