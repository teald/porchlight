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
friendly. To accomplish this, `porchlight` uses CPython standard library to
introspect callable objects for metadata such as variable names, possible
return values, and expected types (using optional Python type hinting). It then
manages the execution of any number of tracked callables, passing required and
updated objects as appropriate. In doing so, it can also track physical
restraints on data, initialize/finalize runs, and update functions defined
dynamically or outside of Python.

# Statement of need

Scientific software has advanced significantly over the last few decades, with
innumerable tools and resources openly available for use by researchers and the
public alike. These software products all undergo unique development lifecycles
tailored to the needs to specific developers.  Although the scientific quality
and usefulness of such products is unquestionable, they often have steep
learning curves that make using and coupling these products difficult to
manage. `porchlight` offers a solution to this problem in the form of a basic
adapter/mediator framework---capable of parsing function metadata, tracking
variable stats, and managing dynamically updating functions, it saves many
lines of code otherwise required to create a simple API or couple to another
disparate piece of software.

## Scientific Modelling

There are an enormous number of scientific models, ranging in size and niche,
and often coupling them together provides useful insight neither could provide
alone. While the intricacies of coupling can be complex, `porchlight`
identifies several typical patterns it seeks to manage:
+ **"I/O" Coupling**: Converting the output of one program to the input of
  another, and vice-versa.
+ **Data Coupling**: Instances of data are modified by different programs.
+ **Evolutionary Coupling**: Functions modify their behavior over time to
  accomodate the state of a previous result.

## Interfacing with scientific models

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

The names of these classes are chosen to be distinct within a given script.
Since "adapter" and "mediator" are common design patterns, it would be foolish
and potentially headache-inducing to call them mroe generic names.



## Outline for this section

1. Describe mediator/adapter scheme
    + What a `Neighborhood` is
    + What a `Door` is
    + Why they have weird names (especially compared to `Param`)
2. Basic use case example?
3. Computational overhead (can give the same response as as AAS I think)
4. Need to mention lack of external dependencies at some point
5. Primary Caveat: Side-effects and functional programming

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
