import param

from unittest import TestCase
import unittest

import itertools

import logging
import os
logging.basicConfig(filename=f"{os.getcwd()}/porchlight_unittest.log")


class ParamTest(TestCase):
    def test___init__(self):
        # Test a variety of inputs.
        names = ("bing", "bong", "bang", "sacrement", "xo xo")
        values = ("testing...", 1, 3.5, 3.e4, tuple(), [1, 2, 3], type)
        constant = (True, False)

        for i, args in enumerate(itertools.product(names, values, constant)):
            cur_param = param.Param(*args)

            self.assertEqual(cur_param.name, args[0])
            self.assertEqual(cur_param.value, args[1])
            self.assertEqual(cur_param.constant, args[2])

    def test___eq__(self):
        param1 = param.Param('x', 1)

        param2 = param.Param('x', 1)

        self.assertEqual(param1, param2)

        param3 = param.Param('x', 2)

        self.assertNotEqual(param1, param3)

        param4 = param.Param('y', 1)

        self.assertNotEqual(param1, param4)

        param5 = param.Param('x', 0)

        self.assertNotEqual(param1, param5)

        param6 = param.Param('x', 1, True)

        self.assertNotEqual(param1, param6)

        nonparam = 'bonk'

        self.assertNotEqual(param1, nonparam)

    def test___str__(self):
        outstr = str(param.Param('x', 1))

        self.assertEqual(outstr, "x (<class 'int'>): 1")

        outstr = str(param.Param('exodia', "bing", True))

        self.assertEqual(outstr, "exodia (<class 'str'>): bing (constant)")

    def test_properties(self):
        # Properties should not be directly mutable.
        testparam = param.Param("hi", 1)

        with self.assertRaises(AttributeError):
            testparam.type = 'bing'

        with self.assertRaises(AttributeError):
            testparam.name = 'bing'

        testparam.value = [1, 2, 3]

        self.assertEqual(testparam.value, [1, 2, 3])

        # This test will fail once Parameter type-checking is enabled.
        self.assertEqual(testparam.type, list)

        # Test constants
        testparam.constant = True

        with self.assertRaises(param.ParameterError):
            testparam.value = 'bing'


class TestEmpty(TestCase):
    def test___eq__(self):
        empty = param.Empty()

        self.assertTrue(empty, param.Empty)
        self.assertTrue(empty, param.Empty())
        self.assertNotEqual(empty, 1)

if __name__ == "__main__":
    unittest.main()
