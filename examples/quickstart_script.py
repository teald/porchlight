"""This script follows the "Quick Start"""
import porchlight


def my_function(x: int, z: int = 0) -> int:
    """This is a simple equation, but we want to return a named variable."""
    y = x ** 2 + z
    return y


neighborhood = porchlight.Neighborhood()  # Instantiates the object.
neighborhood.add_function(my_function)

print(neighborhood)
# Out: Neighborhood(doors={'my_function': Door(name=my_function,
#      base_function=<function my_function at 0x1...F>, arguments={},
#      return_vals=[['y']])}, params={'y': Param(name=y,
#      value=<porchlight.param.Empty object at 0x1...F>, constant=False,
#      type=<class 'porchlight.param.Empty'>)}, call_order=['my_function'])

neighborhood.set_param("x", 2)
neighborhood.set_param("z", 0)

neighborhood.run_step()
print(neighborhood)
# Out: Neighborhood(doors={'my_function': Door(name=my_function,
#      base_function=<function my_function at 0x1...f>, arguments={'x':
#      <class 'int'>, 'z': <class 'int'>}, return_vals=[['y']])}, params={'x':
#      Param(name=x, value=2, constant=False, type=<class 'int'>), 'z':
#      Param(name=z, value=0, constant=False, type=<class 'int'>), 'y':
#      Param(name=y, value=4, constant=False, type=<class 'int'>)},
#      call_order=['my_function'])


def my_new_function(y, z):
    z += y // 2
    return z


neighborhood.add_function(my_new_function)

# Let's run Neighborhood.run_step() a few times and see how the system
# evolves by printing out the parameters.
for i in range(5):
    neighborhood.run_step()

    x = neighborhood.get_value("x")
    y = neighborhood.get_value("y")
    z = neighborhood.get_value("z")

    print(f"{i}) {x = }, {y = }, {z = }")

# Out: 0) x = 2, y = 4, z = 2
# Out: 1) x = 2, y = 6, z = 5
# Out: 2) x = 2, y = 9, z = 9
# Out: 3) x = 2, y = 13, z = 15
# Out: 4) x = 2, y = 19, z = 24

pm = porchlight.Param("x", "hello")
print(pm)

pm.value = "world"
print(pm)

my_constant = porchlight.Param("y", 42.0, constant=True)
pm.constant = True

try:
    pm.value = 10

except Exception as e:
    # Writing out the error and its message.
    print(f"Got {type(e)}: {e}")

# Out: Got <class 'porchlight.param.ParameterError'>: Parameter x is
#      not mutable.


def my_door_to_be(x):
    z = x ** 2
    return z


my_door = porchlight.Door(my_door_to_be)
print(my_door)

# Out: Door(name=my_door_to_be, base_function=<function my_door_to_be at
#      0x1...h>, arguments={'x': <class'porchlight.param.Empty'>},
#      return_vals=[['z']])
