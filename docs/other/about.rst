About |porchlight|
==================

|porchlight| is an open-source function management library designed to aid in
implementing programs with multiple, distinct dependencies.


Background
----------

Originally designed as a part of an unreleased physical and chemical model,
|porchlight| is written primarily from the perspective of a scientific use
case. Well-defined APIs are rare when working with small teams of scientists
and researchers, resulting from a range of factors. This leads to time wasted
in training, implementing, and expanding models with complicated needs.

Instead of outright refactoring, a costly luxury for most research groups,
|porchlight| reframes the problem as one of systems design. Instead of
haphazardly cobbling together a single-use solution involving python scripts,
|porchlight| produces a straightforward interface and automatically manages data
passed between functions as they are executed.

The scope of |porchlight| has expanded considerably since these initial ideas.
While still in active development, it already has solid use cases outside the
halls of science.

Example use cases
-----------------

-  Pseudo-control external access to shared data.
-  Automate coupling models with shared, evolving parameter sets.
-  Set parameter limits to catch unique error cases, such as unphysical
   conditions or numerical instabilities.
-  Couple models in a single, short script, without hand-managing input files or
   writing long single-use automation scripts.
-  Provides a basic API for making development and research more accessible to
   early developers.

FAQ
---

1. Why is it called |porchlight|?

   -  |porchlight| was decided on to be reminiscent of illumination and
      community; it aims to help others make incredible things and to "bring
      light" to the doorsteps of otherwise inaccessible models. Most
      importantly; it was available on the Python Package Index at the time and
      is relatively memorable.

2. Why does everything have regular noun names, like
   :class:`~porchlight.door.Door` or
   :class:`~porchlight.neighborhood.Neighborhood`?

   -  To match the name of the software + to provide clear visualization of how
      the objects function. That said, |porchlight| is still in alpha so it
      could change by beta!

3. Why should I use |porchlight|? Are there situations where I *shouldn't* use
   it?

   -  You *should use* this if you:

     -  Are looking for something to make getting from an interesting
        question/idea to implementing and testing that idea ASAP.
     -  Coupling different programs together for specific use cases.
     -  Expanding your own code without writing new, specific implementations
        for integrating new software.
     -  Need a quick, basic API for an otherwise complex input/output system.

   -  You *should consider other options* if you're looking for:

      -  A permanent solution for poorly designed codebases. While in spirit
         |porchlight| is meant to circumvent hardships weird APIs (or complete
         lack of any supported API) present to hitting the ground running
         without micromanagement.
      -  Threading/multiprocessing manager.
      -  Static or partially-static typing schemes (use `mypy` or another strict
         typing checker).

.. |porchlight| replace:: **porchlight**
