---
title: '`porchlight`: an open-source function management and coupling tool'
tags:
  - Python
  - applications
  - general purpose
  - utility
  - software accessibility
authors:
  - name: D. J. Teal
    orcid: 0000-0002-1912-3057
    affiliation: "1, 2" # (Multiple affiliations must be quoted)
affiliations:
 - name: University of Maryland, College Park
   index: 1
 - name: NASA Goddard Space Flight Center
date: 01/27/2023
bibliography: paper.bib

---

# Summary

`porchlight` is an Python function management and coordination package designed
to make coupling disparate models straigthforward, portable, and end-user
friendly. To accomplish this, `porchlight` uses CPython standard library
introspection methods to introspect callable objects for metadata such as
variable names, possible return values, and expected types (using optional
Python type hinting). It then manages the execution of any number of tracked
callables, passing required and updated objects as appropriate. In doing so, it
can also track physical restraints on data, initialize/finalize runs, and
update functions defined dynamically or outside of Python.

# Statement of need

Scientific software has advanced significantly over the last few decades, with
innumerable tools and resources openly available for use by researchers and the
public alike. These software products all undergo unique development lifecycles
tailored to the needs to specific developers.  Although the scientific quality
and usefulness of such products is unquestionable, they often have steep
learning curves that make using and coupling these products difficult to
manage. `porchlight` offers a low-level solution to this problem in the form of
a basic adapter/mediator framework---capable of parsing function metadata,
tracking object states, and managing dynamically updating functions. It also
results in a rudimentary API, usable by novice Python users without the need to
interact with any component model(s).

## Scientific Modelling

There are an enormous number of scientific models, ranging in size and niche,
and coupling them together often provides useful insight neither could alone.
While the intricacies of coupling can be complex, `porchlight` identifies
several typical patterns it seeks to manage, defined in Table 1 below.

| **Term** | **Definition** |
| :--- | :--------- |
| **I/O Coupling** | Converting output of one program to the input of another. |
| **Data Coupling** | Instances of data (objects) are modified by different programs during runtime |
| **Evolutionary Coupling** | Functions modify their behavior and requirements to accomodate a changing model state |

Too often, solutions to these coupling problems can be time-consuming and
difficult to structure. In the worst cases, it may hamper the reproducibility
of a result or understanding of model interactions. With `porchlight`, the
coupled-model structure is pre-defined, and the user requirements are minimal:

1. The model or effect being integrates can be defined as a Python function.
2. These Python functions have unique names for unique variables, and shared
   names for shared variables.
3. The return values of these functions---if they exist---correspond to new
   data to be stored by porchlight, or to extant data changed by the model
   function.

## Interfacing with scientific models and model accessibility

Another common pattern in the research software development lifecycle is
re-development to create an application programming interface (API) for a
useful codebase. Ideally, model development leads to a well-considered API.
This is a challenging feat, though, without exceptional experience creating
such software.

`porchlight`'s management system acts as an out-of-the-box API for many
use-cases, and can be tailored to as-specific a niche as needed with minimal
effort. This is detailed in [[TKREFERENCESECTION]].


# Design Schematics

`porchlight` is designed using a mediator class (`Neighborhood`) and an adapter
class (`Door`). These objects together manage coupling and introspection to
produce a basic API interface with some arbitrarily complex and inter-dependent
set of functions.

Given an arbitrary Python function, `f(x_1, x_2, ..., x_n)`, a `Door` will
first use standard library inspection methods---via the `inspect` module---to
determine the arguments types (keyword vs positional) and any default values.
Then, source lines for the function are re-parsed to determine if any return
values contain keywords. **FOOTNOTE: Need to explain this and its
restrictions.**

This door is then provided to a `Neighborhood` object, which tracks inputs and
outputs to these functions, passing them between doors and to the user.

The names of these classes are chosen to be distinct within a given script. To
provide descriptive names as well, `Neighborhood` is aliased to
`PorchlightMediator`, and `Door` to `PorchlightAdapter`, including objects with
those prefixes [[TKIMPLEMENTING]].

## Dependencies and overhead

The `porchlight` library, including its unit tests, to not require anything
beyond the standard CPython library.

`porchlight` does not add considerable overhead to execution, assuming
functional definitions are not disturbingly long. The frequency of tests being
executed between model runs is something to consider when using `porchlight`
with physical checks. For example, if I check `temperature` to ensure the value
is always positive, that check will occur whenever `temperature` is modified by
a function or returned. This is left to the users' needs and preferences.

## Side Effects

As an object-oriented programming language, the modification of objects during
code execution is a foundational design of the Python language and how it
works. Side-effects, oversimplified here as any change to the state of any
number of objects during the execution of a function, is common across various
implementations and use cases. For example, the below function `upper_name` has
2 side-effects: the input argument `name` is given the token `is_cached`, and
another external variable `name_cache` is updates.

```python
name_cache = dict()

class Name:
    def __init__(self, name: str):
        self.is_cached = (name in name_cache)
        self.str = name

    def __str__(self):
        return self.str

def upper_name(name: Name):
    if not name.is_cached:
        name_cache[str(name)] = str(name).upper()

    return name_cache[str(name)]

name = Name("hi there")

print(upper_name(name))
```

This is not a design flaw. It can, however, quickly produce problems when not
well-understood by a novice user of a software suite. In the context of
`porchlight`, especially when implemented as a part of software using
side-effects during execution. Although tools to assist in identifying possible
sources of undesirable side-effects are under development, they are
experimental and not available in the current release of `porchlight`.

# Citations

Citations to entries in paper.bib should be in
[rMarkdown](http://rmarkdown.rstudio.com/authoring_bibliographies_and_citations.html)
format.

If you want to cite a software repository URL (e.g. something on GitHub without
a preferred citation) then you can do it with the example BibTeX entry below
for @fidgit.

For a quick reference, the following citation commands can be used:
- `@author:2001`  ->  "Author et al. (2001)"
- `[@author:2001]` -> "(Author et al., 2001)"
- `[@author1:2001; @author2:2001]`
    -> "(Author1 et al., 2001; Author2 et al., 2002)"

# Figures

Figures can be included like this:
![Caption for example figure.\label{fig:example}](figure.png)
and referenced from text using \autoref{fig:example}.

Figure sizes can be customized by adding an optional second parameter:
![Caption for example figure.](figure.png){ width=20% }

# Acknowledgements

This work was partially funded by NSF [[TKGRANTINFO]]. Special thanks to Nathan
LaPr&eacute; for extensive discussions on design and implementation.
[[TKPEOPLEWHOPROOFREADTHIS]]


# References
