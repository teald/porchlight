"""Tests for functions contained in ../utils/typing_functions."""
from porchlight.utils import typing_functions
from typing import Callable, Dict, Tuple

import unittest


class TestTypingFunctions(unittest.TestCase):
    def test_decompose_type(self):
        # TODO: The below should be reorganized to have tests go from defaults
        # -> messing with parameters. Right now, confusing that
        # include_base_types == True isn't covered until after other test
        # cases.
        # Define test cases as input/expected output pairs.
        test_cases = (
            ([str], [str]),
            ([Tuple], [Tuple]),
            ([Tuple[str]], [str]),
            ([Dict[str, list]], [str, list]),
            ([Tuple[Callable[str, float], str]], [Callable[str, float], str]),
        )

        for test in test_cases:
            decomposition = typing_functions.decompose_type(
                *test[0], [], False
            )

            self.assertEqual(decomposition, test[1])

        # Examples with break_types != []
        test_cases = (
            ([str, [float]], [str]),
            ([Tuple, [Tuple]], [Tuple]),
            ([Tuple[str], [Tuple]], [Tuple[str]]),
            ([Dict[str, list[str]], [list]], [str, list[str]]),
            ([Callable[str, float], [Callable]], [Callable[str, float]]),
        )

        for test in test_cases:
            decomposition = typing_functions.decompose_type(*test[0], False)

            self.assertEqual(decomposition, test[1])

        # Examples with include_base_types = True
        test_cases = (
            ([str, []], [str]),
            ([Tuple, []], [Tuple]),
            ([Tuple[str], []], [Tuple[str], str]),
            (
                [Dict[str, list[str]], []],
                [Dict[str, list[str]], str, list[str]],
            ),
            ([Callable[str, float], []], [Callable[str, float]]),
        )

        for test in test_cases:
            decomposition = typing_functions.decompose_type(*test[0])

            self.assertEqual(decomposition, test[1])


if __name__ == "__main__":
    # Run test
    unittest.main()
