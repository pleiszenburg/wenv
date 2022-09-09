# How to contribute to *wenv*

Thank you for considering contributing to *wenv*!
**Contributions are highly welcomed!**

## Branching model

Development happens in the `develop` branch. Please issue pull requests against `develop`. The `master` branch is supposed to be kept at the latest, stable *release*.

## Language level & interpreters

This project targets Python 3 exclusively. The primary target so far is CPython, although PyPy support is highly welcome.

## Dependencies

Keep them to a minimum, i.e. none. This is important for the `zugbruecke` package, which depends on `wenv`.

## General workflow

If you are planning on working on a "larger" issue or feature, please add yourself to the corresponding issue on GitHub or create a new one there - before you start working. This helps to reduce duplicate effort and allows to coordinate developers.

New features are supposed to be tested. Tests are expected as part of pull requests.
