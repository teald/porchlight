About `porchlight`
==================

Functionality
-------------

* Control external access to shared data.
* Automate coupling models with shared, evolving parameter sets.
* Set parameter limits to catch unique error cases, such as unphysical
  conditions or numerical instabilities.
* Couple models in a single, short script, without hand-managing input files or
  writing long single-use automation scripts.
* Provides a basic API for making development and research more accessible to
  early developers.

FAQ
---

1. Why is it called `porchlight`?
  - `porchlight` was decided on to be reminiscent of illumination and
    community; it aims to help others make incredible things and to "bring
    light" to the doorsteps of otherwise inaccessible models. Most importantly;
    it was available on the Python Package Index at the time and is relatively
    memorable.
2. Why does everything have regular noun names, like
   :class:`~porchlight.door.Door` or
   :class:`~porchlight.neighborhood.Neighborhood`?
  - To match the name of the software + to provide clear visualization of how
    the objects function. That said, `porchlight` is still in alpha so it could
    change by beta!
3. Why should I use `porchlight`? Are there situations where I *shouldn't* use
   it?
  - You *should use* this if you're:
    -  Looking for something to make getting from an interesting question/idea
       to implementing and testing that idea ASAP.
    -  Coupling different programs together for specific use cases.
    -  Expanding your own code without writing new, specific implementations
       for integrating new software.
    -  Need a quick, basic API for an otherwise complex input/output system.
  - You *should consider other options* if you're looking for:
    - A permanent solution for poorly designed codebases. While in spirit
      `porchlight` is meant to circumvent hardships weird APIs (or complete
      lack of and API) present to hitting the ground running without coupling
      models.
    - Threading/multiprocessing manager.
    - Static or partially-static typing schemes (use `mypy` or another strict
      typing checker).
