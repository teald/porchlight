"""Unit testing for porchlight/utils/inspect_functions."""
import porchlight.utils.inspect_functions as inspect_functions
import inspect
import unittest


def _helper_indent_and_newline(
    lines: list[str], indent: int, indent_blank: bool = True
):
    """Takes a list of strings and returns those strings."""
    for i, line in enumerate(lines):
        if line:
            line = " " * indent + line

        if i < len(lines):
            line += "\n"

        lines[i] = line

    return lines


class TestInspectFunctions(unittest.TestCase):
    def test_get_all_source(self):
        # The baseline case should reduce directly to inspec.getsourcelines
        def test1(bing_bong: bool = True) -> str:
            """This is my internal docstring."""
            switch = bing_bong

            # This is a comment line.
            result = "The switch is "
            result += "on" if switch else "off"

            return result

        expected_result = inspect.getsourcelines(test1)

        result = inspect_functions.get_all_source(test1)

        self.assertEqual(result[0], expected_result[0])
        self.assertEqual(result[1], expected_result[1])

        # Decorator handling.
        def test2_decorator(fxn):
            """This is a dummy wrapper."""

            def wrapper(*args, **kwargs):
                result = fxn(*args, **kwargs)
                return result

            return wrapper

        @test2_decorator
        def test2(a, b, c):
            """A docstring for this test function."""
            # A comment in this test function.
            total = sum(a, b, c)
            outstr = f"{total} = {a} + {b} + {c}"
            return outstr

        expected_result = [
            "@test2_decorator",
            "def test2(a, b, c):",
            '    """A docstring for this test function."""',
            "    # A comment in this test function.",
            "    total = sum(a, b, c)",
            '    outstr = f"{total} = {a} + {b} + {c}"',
            "    return outstr",
        ]

        expected_result = _helper_indent_and_newline(expected_result, 8)

        result = inspect_functions.get_all_source(test2)
        self.assertEqual(result[0], expected_result)

        # Decorators with arguments.
        def test3_decorator(message):
            def test3_decorator(fxn):
                def wrapped_fxn(*args, **kwargs):
                    result = fxn(*args, **kwargs)
                    return f"{message}\n{result}"

                return wrapped_fxn

            return test3_decorator

        @test3_decorator("This was a unit test: ")
        def test3(*vector_values):
            vector = [f"{x:1.3e}" for x in vector_values]
            vectorstr = "".join(vector)

            return vectorstr

        expected_result = [
            '@test3_decorator("This was a unit test: ")',
            "def test3(*vector_values):",
            '    vector = [f"{x:1.3e}" for x in vector_values]',
            '    vectorstr = "".join(vector)',
            "",
            "    return vectorstr",
        ]

        expected_result = _helper_indent_and_newline(expected_result, 8)

        result = inspect_functions.get_all_source(test3)
        self.assertEqual(result[0], expected_result)

        # With multiple decorators.
        def test4_dec1(fxn):
            def wrapper1(*args, **kwargs):
                result = fxn(*args, **kwargs)
                return result

            return wrapper1

        def test4_dec2(fxn):
            def wrapper2(*args, **kwargs):
                result = fxn(*args, **kwargs)
                return result

            return wrapper2

        @test4_dec1
        @test4_dec1
        def test4_1():
            pass

        expected_result = [
            "@test4_dec1",
            "@test4_dec1",
            "def test4_1():",
            "    pass",
        ]

        expected_result = _helper_indent_and_newline(expected_result, 8)
        result = inspect_functions.get_all_source(test4_1)

        self.assertEqual(result[0], expected_result)

        @test4_dec1
        @test4_dec2
        def test4_2():
            pass

        expected_result = [
            "@test4_dec1",
            "@test4_dec2",
            "def test4_2():",
            "    pass",
        ]

        expected_result = _helper_indent_and_newline(expected_result, 8)
        result = inspect_functions.get_all_source(test4_2)

        self.assertEqual(result[0], expected_result)

    def test_non_callable(self):
        tests = [1, "2", {3: 4}]

        for test in tests:
            with self.assertRaises(TypeError):
                inspect_functions.get_all_source(test)

            with self.assertRaises(TypeError):
                inspect_functions.get_wrapped_function(test)


if __name__ == "__main__":
    unittest.main()
