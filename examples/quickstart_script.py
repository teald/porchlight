"""This script follows the "Quick Start"""
import porchlight


def my_function(x: int, z: int = 0) -> int:
    """This is a simple equation, but we want to return a named variable."""
    y = x ** 2 + z
    return y


neighborhood = porchlight.Neighborhood()  # Instantiates the object.
neighborhood.add_function(my_function)

print(neighborhood)
# >>> Neighborhood(doors={'my_function': Door(name=my_function,
#     base_function=<function my_function at 0x1...F>, arguments={},
#     return_vals=[['y']])}, params={'y': Param(name=y,
#     value=<porchlight.param.Empty object at 0x1...F>, constant=False,
#     type=<class 'porchlight.param.Empty'>)}, call_order=['my_function'])

neighborhood.set_param("x", 2)
neighborhood.set_param("z", 0)

neighborhood.run_step()
print(neighborhood)
# >>> Neighborhood(doors={'my_function': Door(name=my_function,
#     base_function=<function my_function at 0x1...f>, arguments={'x':
#     <class 'int'>, 'z': <class 'int'>}, return_vals=[['y']])}, params={'x':
#     Param(name=x, value=2, constant=False, type=<class 'int'>), 'z':
#     Param(name=z, value=0, constant=False, type=<class 'int'>), 'y':
#     Param(name=y, value=4, constant=False, type=<class 'int'>)},
#     call_order=['my_function'])


def my_new_function(y, z):
    z += y // 2
    return z


neighborhood.add_function(my_new_function)
neighborhood.run_step()

print(neighborhood)

for param in neighborhood.params.values():
    print(param)
    # >>> Neighborhood(doors={'my_function': Door(name=my_function,
    #     base_function=<function my_function at 0x1..f>, arguments={'x':
    #     <class 'int'>, 'z': <class 'int'>}, return_vals=[['y']])},
    #     params={'x': Param(name=x, value=2, constant=False, type=<class
    #     'int'>), 'z': Param(name=z, value=0, constant=False, type=<class
    #     'int'>), 'y': Param(name=y, value=4, constant=False, type=<class
    #     'int'>)},
    # call_order=['my_function'])
    # >>> Param(name=x, value=2, constant=False, type=<class 'int'>)
    # >>> Param(name=z, value=0, constant=False, type=<class 'int'>)
    # >>> Param(name=y, value=4, constant=False, type=<class 'int'>)
