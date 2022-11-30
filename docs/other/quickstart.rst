Quickstart
==========

Welcome to a short guide to hitting the ground running with `porchlight`! This
tutorial will step through the basics of installing and using `porchlight`. If
you are looking for more advanced examples, see the examples availabe in our
`github repository <https://github.com/teald/porchlight/tree/main/examples>`.

Requirements
------------

`porchlight` requires *Python version 3.9 or higher*.


Installation
------------

For help installing Python 3.9 or above please see their respective
instructions:

* `Python 3.9 or above <https://www.python.org/downloads/>`

You can install `porchlight` directly using `pip`:

.. code-block:: console
    :caption: pip installation
    pip install porchlight


 Once porchlight has installed, you're ready to start writing code. If you'd
 like, this guide can be followed line-for-line in an interactive python
 environment! To get started, just import the library:

..code-block:: python
    import porchlight

Creating a `Door` object
========================

The `Door` class acts as an interface (an "open door") to the internals of a
python function object. To create one, we just need to import porchlight
and
