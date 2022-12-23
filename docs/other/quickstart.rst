.. role:: python(code)
   :language: python

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

* `Python 3.9 or above <https://www.python.org/downloads/>`_

You can install |porchlight| directly using :code:`pip`:

.. code-block:: console

    pip install porchlight

Once |porchlight| has installed, you're ready to start writing code. If you'd
like, this guide can be followed line-for-line in an interactive python
environment! To get started, just import the library:

.. code-block:: python

   import porchlight

Type annotations and |porchlight|
---------------------------------

Within |porchlight|, type annotation are allowed and encouraged. Generally, save
for a few *very special cases*, you can ignore type annotations when writing
your code. |porchlight|, via the |Door| class in particular, will note type
annotations if they are present and otherwise will ignore them.

Creating a |Neighborhood| object
--------------------------------

The |Neighborhood| object collects various
functions, extracts information about the function from existing metadata
(using the `inspect <https://docs.python.org/3/library/inspect.html>`_ module
in the CPython standard library) and the source code itself. Adding a function
to a

.. code-block:: python

   def my_function(x: int, z: int = 0) -> int:
       '''This is a simple equation, but we want to return
       a named variable.
       '''
       y = x ** 2 + z
       return y


   neighborhood = porchlight.Neighborhood()  # Instantiates the object.
   neighborhood.add_function(my_function)

At this point, |porchlight| will parse the function and store metadata about
it. The `str` representation of Neighborhood contains most of the data:

.. code-block:: python

    print(neighborhood)

::

    Neighborhood(doors={'my_function': Door(name=my_function, base_function=<function my_function at 0x1...F>, arguments={}, return_vals=[['y']])}, params={'y': Param(name=y, value=<porchlight.param.Empty object at 0x1...F>, constant=False, type=<class 'porchlight.param.Empty'>)}, call_order=['my_function'])

A few things are now kept track of by the |Neighborhood| automatically:

1. The function arguments, now tracked as a |param| object. The default values
   found were saved (in our case, it found `z = 0`), and any parameters not yet
   assigned a value have been given the :py:class:`~porchlight.param.Empty`
   value.
2. Function return variables. We'll explore this in more detail later, but one
   important note here: the return variable name is important!

Right now, our |Neighborhood| is a
fully-fledged, if tiny, model. Let's set our variables and run it!

.. code-block:: python

   neighborhood.set_param('x', 2)
   neighborhood.set_param('z', 0)

   neighborhood.run_step()
   print(neighborhood)

::

    Neighborhood(doors={'my_function': Door(name=my_function, base_function=<function my_function at 0x1...f>, arguments={'x': <class 'int'>, 'z': <class 'int'>}, return_vals=[['y']])}, params={'x': Param(name=x, value=2, constant=False, type=<class 'int'>), 'z': Param(name=z, value=0, constant=False, type=<class 'int'>), 'y': Param(name=y, value=4, constant=False, type=<class 'int'>)}, call_order=['my_function'])


:py:meth:`~porchlight.neighborhood.Neighborhood.run_step` executes all
functions that have been added to our |Neighborhood| object. The object passes
the parameters with names matching the arguments in :code:`my_function`, and
stores :code:`my_function`'s output in the parameter for :code:`y`.

All of this could be accomplished in a few lines of code without any imports,
obviously. We could manage our own :code:`x`, :code:`y`, and :code:`z` in a
heartbeat, and all |porchlight| *really* did was what we could do with
something as simple as :python:`y = my_function(2, 0)`. Let's add another
function to our neighborhood and call
:meth:`~porchlight.neighborhood.Neighborhood.run_step`

.. code-block:: python

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

::

    0) x = 2, y = 4, z = 2
    1) x = 2, y = 6, z = 5
    2) x = 2, y = 9, z = 9
    3) x = 2, y = 13, z = 15
    4) x = 2, y = 19, z = 24

As we see, we are now running a system of two functions that share variables.
As we step forward, the functions are called sequentially and the parameters
are updated directly.

Behind the scenes, our |Neighborhood| object has generated a number of |Door|
objects and |Param| objects that hold onto metadata our |Neighborhood| can use
to know when and what to run, check, and modify. To really leverage
|porchlight|, we'll need to get to know these objects a bit better on their
own.

|Param| objects
---------------

|Param| objects manage the memory being passed between functions in our
|Neighborhood| object.

These are pretty simple objects, and making them is also simple:

.. code-block:: python

   pm = porchlight.Param("x", "hello")

::

    Param(name=x, value=hello, constant=False, type=<class 'str'>)

To access the data of a |Param|, you need to get its :python:`.value`
attribute. To change the value, we can update the value directly using
something like

.. code-block:: python

   pm.value = "world"
   print(pm)

::

    Param(name=x, value=world, constant=False, type=<class 'str'>)

We can also specify that parameters should be constant, or change parameters to
become constant.

.. code-block:: python

    my_constant = porchlight.Param("y", 42.0, constant=True)
    pm.constant = True

    try:
        pm.value = 10

    except Exception as e:
        # Writing out the error and its message.
        print(f"Got {type(e)}: {e}")

::

    Got <class 'porchlight.param.ParameterError'>: Parameter x is not mutable.

This is great for keeping parameters that should stay constant for a specific
scenario constant. Keep in mind that |Param| implemented like this is not a
true constant, like ``const`` in other programming languages. The data could
*still be modified as a side effect of functions*.

Within our |Neighborhood|, we've already seen param basics. We can add our own
params or modify the existing ones in a few different ways, the safest of which
is to use :py:meth:`~porchlight.neighborhood.Neighborhood.set_param`, which we
used above.

Now, let's turn to how our |Neighborhood| re-interprets our function
definitions to know what to pass to them.

|Door| objects
--------------

A |Door| is an object that contains metadata about how to call a function and
what it might return.

Because we can return quite a few things, including evaluated expressions in
the return statement, |Door| objects will not consider outputs that are not
valid Python variable names.

.. code-block:: python

    my_door = porchlight.Door(my_door_to_be)
    print(my_door)

::

    Door(name=my_door_to_be, base_function=<function my_door_to_be at 0x1...h>, arguments={'x': <class'porchlight.param.Empty'>}, return_vals=[['z']])

So far, we've defined the functions we'll be working with ourselves, but what
if we want to include a function from a library or source with incompatible
definitions? With our |Door| we can map function argument/return value names to
match our needs. In our example, say we are given the following function from a
coworker that they want integrated into the model we already have:

.. code-block:: python

   def coworker_function(a, b=0):
       b = b + a // b
       a = a + 1
       return a, b

We would need to write our own function that converts our ``x`` and ``y`` into
``a`` and ``b`` if we wanted to pass a representation of this function to
|Door| like we have been. We can pass the keyword argument
:code:`argument_mapping` when we initialize our door, though, to signal that
these variables should be treated like they have different names.

.. code-block:: python

   my_coworker_door = porchlight.Door(
       coworker_function, argument_mapping={'x': 'a', 'y': 'b'}
   )

Now, our |Door| :code:`my_coworker_door` will take ``x`` and ``y`` as
arguments, and |Neighborhood| objects can recognize this. Let's add our new
door to our :code:`neighborhood`.

.. code-block:: python

   neighborhood.add_door(my_coworker_door)

   for i in range(5, 10):
       neighborhood.run_step()

       x = neighborhood.get_value("x")
       y = neighborhood.get_value("y")
       z = neighborhood.get_value("z")

       print(f"{i}) {x = }, {y = }, {z = }")

::

   5) x = 3, y = 29, z = 38
   6) x = 4, y = 48, z = 61
   7) x = 5, y = 78, z = 99
   8) x = 6, y = 125, z = 161
   9) x = 7, y = 198, z = 259

And now, with just 2 lines of code, we've fully integrated our coworker's code
into our own! You could keep doing this with as many functions as you'd like;
as long as they're convertible to a |Door|, our |Neighborhood| will keep
accepting new functions.

This is the end of the interactive portion of the Quickstart Guide. With the
knowledge you have now, you are more than capable of doing some pretty exciting
things with |porchlight|! That said, keep in mind there *is* more to the
package, as well as some nuances.

Closing Nuances
---------------

-  |Neighborhood| objects will execute their functions sequentially, in the
   order they are added. if you'd like to re-order the functions before
   execution, see :py:meth:`~porchlight.neighborhood.Neighborhood.order_doors`.

- |porchlight| is under active development. The current development strategy
  will not include a dedicated stable branch until v1.0.0. That means that you
  need to be cautious with versions before v1.0.0, and some changes may break
  your code. You can generally assume that increments of 0.0.1 are non-breaking.
  0.1.0 increments may be breaking.

.. |porchlight| replace:: **porchlight**
.. _Python: https://www.python.org/downloads/
.. |Neighborhood| replace:: :py:class:`~porchlight.neighborhood.Neighborhood`
.. |Door| replace:: :py:class:`~porchlight.door.Door`
.. |Param| replace:: :py:class:`~porchlight.param.Param`
