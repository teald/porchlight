Quickstart
==========

Welcome to a short guide to hitting the ground running with |porchlight|! This
tutorial will step through the basics of installing and using |porchlight|. If
you are looking for more advanced examples, see the examples available in
`the porchlight github repository <https://github.com/teald/porchlight/tree/main/examples>`_.

Requirements
------------

|porchlight| requires *Python version 3.9 or higher*.


Installation
------------

For help installing Python 3.9 or above please see their respective
instructions:

* :ref:`Python 3.9 or above<Python_>`

You can install |porchlight| directly using ``pip``:

.. testcode:: console

    pip install porchlight

Once porchlight has installed, you're ready to start writing code. If you'd
like, this guide can be followed line-for-line in an interactive python
environment! To get started, just import the library:

.. testcode:: python

    import porchlight

Type annotations and |porchlight|
--------------------------------

Within |porchlight|, type annotation are allowed and encouraged. Generally, save
for a few *very special cases*, you can ignore type annotations when writing
your code. |porchlight|, via the |Door| class in particular, will note type
annotations if they are present and otherwise will ignore them.

Creating a |Neighborhood| object
----------------------------------

The |Neighborhood| object collects various
functions, extracts information about the function from existing metadata
(using the `inspect <https://docs.python.org/3/library/inspect.html>`_ module
in the CPython standard library) and the source code itself. Adding a function
to a

.. testcode:: python

    def my_function(x: int, z: int = 0) -> int:
        '''This is a simple equation, but we want to return a named variable.'''
        y = x ** 2 + z
        return y


    neighborhood = porchlight.Neighborhood()  # Instantiates the object.
    neighborhood.add_function(my_function)

At this point, |porchlight| will parse the function and store metadata about
it. The `str` representation of Neighborhood contains most of the data:

.. testcode:: python

    print(neighborhood)
    # >>  Neighborhood(doors={'my_function': Door(name=my_function, base_function=<function my_function at 0x1...F>, arguments={}, return_vals=[['y']])}, params={'y': Param(name=y, value=<porchlight.param.Empty object at 0x1...F>, constant=False, type=<class 'porchlight.param.Empty'>)}, call_order=['my_function'])

A few things are now kept track of by the |Neighborhood| automatically:

1. The function arguments, now tracked as a |param| object. The default values
   found were sazed (in our case, it found `z = 0`), and any parameters not yet
   assigned a value have been given the :py:class:`~porchlight.param.Empty`
   value.
2. Function return variables. We'll explore this in more detail later, but one
   important note here: the return variable name is important!

Right now, our |Neighborhood| is a
fully-fledged, if tiny, model. Let's set our variables and run it!

.. testcode:: python
    neighborhood.set_param('x', 2)
    neighborhood.set_param('z', 0)

    neighborhood.run_step()
    print(neighborhood)
    # Neighborhood(doors={'my_function': Door(name=my_function, base_function=<function my_function at 0x1...f>, arguments={'x': <class 'int'>, 'z': <class 'int'>}, return_vals=[['y']])}, params={'x': Param(name=x, value=2, constant=False, type=<class 'int'>), 'z': Param(name=z, value=0, constant=False, type=<class 'int'>), 'y': Param(name=y, value=4, constant=False, type=<class 'int'>)}, call_order=['my_function'])

:py:func:`~porchlight.neighborhood.Neighborhood.run_step` executes all
functions that have been added to our |Neighborhood| object. The object passes
the parameters with names matching the arguments in ``my_function``, and stores
``my_function``'s output in the parameter for ``y``.

All of this could be accomplished in a few lines of code without any imports,
obviously. We could manage our own ``x``, ``y``, and ``z`` in a heartbeat, and all
|porchlight| *really* did was what we could do with something as simple as
``y = my_function(2, 0)``. Let's add another function to our neighborhood and
call :func:`~porchlight.neighborhood.Neighborhood.run_step`

.. testcode:: python

    def my_new_function(y, z):
        z += y // 2
        return z

    neighborhood.add_function(my_new_function)

    # Let's run Neighborhood.run_step() a few times and see how the system
    # evolves by printing out the parameters.
    for i in range(5):
        neighborhood.run_step()

        x = neighborhood.get_value('x')
        y = neighborhood.get_value('y')
        z = neighborhood.get_value('z')

        print(f"{i}) {x = }, {y = }, {z = }")

    # >>> 0) x = 2, y = 4, z = 2
    # >>> 1) x = 2, y = 6, z = 5
    # >>> 2) x = 2, y = 9, z = 9
    # >>> 3) x = 2, y = 13, z = 15
    # >>> 4) x = 2, y = 19, z = 24

As we see, instead of having to write our own script and manage variables, we
are now running a system of two functions that share variables. As we step
forward, the functions are called sequentially and the parameters are updated
directly.

Behind the scenes, our |Neighborhood| object has generated a number of |Door|
objects and |Param| objects

.. |porchlight| replace:: ``porchlight``
.. _Python: https://www.python.org/downloads/
.. |Neighborhood| replace:: :py:class:`porchlight.neighborhood.Neighborhood`
.. |Door| replace:: :py:class:`~porchlight.door.Door`
.. |Param| replace:: :py:class:`~porchlight.param.Param`