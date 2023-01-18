<img src="docs/source/porchlight_logo.gif" width="200" height="200" alt="porchlight logo. A snake's head erupts from the bottom of a porchlight casing, reaching towards a spinning triangular pyramid. The pyramid radiates bright, saturated, multicolored light." style="float:left" />

[porchlight](https://porchlight.readthedocs.io/en/latest/)
==========

`porchlight` is a function management suite that handles shared inputs and
outputs of methods and/or functions which evolve over the lifetime of a program.

This package's original intent was to be a part of a modular scientific package
yet to be released. Rather than isolating this method to a single model, the
already-developed work has been modified to stand alone as a package.

`porchlight` does not have any dependencies outside of the standard CPython
library. Please note that `porchlight` requires Python 3.9\+, and that examples
may require external libraries such as `numpy` and `matplotlib`.

Installation
------------

You can install `porchlight` by cloning this repository to a local directory.
Alternatively, you may use `pip` in the command line:
```console
pip install porchlight
```

Usage
-----

The main object used in `porchlight` is the `porchlight.Neighborhood` object.
This groups all functions together and keeps track of call order and
parameters.

```python
import porchlight


# To add a function, we simply define it and pass it to porchlight.
def increase_x(x: int, y: int) -> int:
    x = x * y
    return x

# Type annotations are optional, as with normal python.
def string_x(x):
    x_string = f"{x = }"
    return x_string

def increment_y(y=0):
    y = y + 1
    return y

# Generating a complete, coupled model between these functions is as simple as
# adding all these functions to a Neighborhood object.
neighborhood = Neighborhood([increment_y, increase_x, string_x])

# The neighborhood object inspects the function, finding input and output
# variables if present. These are added to the collections of functions and
# parameters.
print(neighborhood)

# We initialize any variables we need to (in this case, just x), and then
# executing the model is a single method call.
neighborhood.set_param('x', 2)

neighborhood.run_step()

# Print out information.
for name, param in neighborhood.params.items():
    print(f"{name} = {param}")
```

Documentation
-----------

Documentation for `porchlight` can be found on Read the Docs here: https://porchlight.readthedocs.io/en/latest/

Other info
----------

+ You can find slides from presentations about porchlight within the `docs` folder, under [`docs/slides`](https://github.com/teald/porchlight/tree/main/docs/slides).
