from porchlight import Neighborhood


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
neighborhood.set_param("x", 2)

neighborhood.run_step()

# Print out information.
for name, param in neighborhood.params.items():
    print(f"{name} = {param}")
