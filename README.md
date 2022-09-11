![wenv](docs/source/_static/logo.png "wenv logo")

# wenv - Running Python on Wine

[![build_master](https://github.com/pleiszenburg/wenv/actions/workflows/test.yaml/badge.svg?branch=master "Build Status: master / release")](https://github.com/pleiszenburg/wenv/actions/workflows/test.yaml)
[![docs_master](https://readthedocs.org/projects/wenv/badge/?version=latest&style=flat-square "Documentation Status: master / release")](https://wenv.readthedocs.io/en/latest/)
[![license](https://img.shields.io/pypi/l/wenv.svg?style=flat-square "GNU Lesser General Public License v2.1")](https://github.com/pleiszenburg/wenv/blob/master/LICENSE)
[![status](https://img.shields.io/pypi/status/wenv.svg?style=flat-square "Project Development Status")](https://github.com/pleiszenburg/wenv/issues)
[![pypi_version](https://img.shields.io/pypi/v/wenv.svg?style=flat-square "Project Development Status")](https://pypi.python.org/pypi/wenv)
[![pypi_versions](https://img.shields.io/pypi/pyversions/wenv.svg?style=flat-square "Available on PyPi - the Python Package Index")](https://pypi.python.org/pypi/wenv)
[![chat](https://img.shields.io/matrix/zugbruecke:matrix.org.svg?style=flat-square "Matrix Chat Room")](https://matrix.to/#/#zugbruecke:matrix.org)
[![mailing_list](https://img.shields.io/badge/mailing%20list-groups.io-8cbcd1.svg?style=flat-square "Mailing List")](https://groups.io/g/zugbruecke-dev)

## Synopsis

**wenv** is a **Python package** (currently in development **status 4/beta**). It allows to **run Python on top of Wine** on Linux, MacOS or BSD. It handles required plumbing related to making Python and a number of Python modules work on Wine. `wenv` creates isolated virtual environments which can be transparently used from a Unix command line and which seamlessly integrate into Unix Python virtual environments.

About Wine (from [winehq.org](https://www.winehq.org/)): *Wine (originally an acronym for "Wine Is Not an Emulator") is a compatibility layer capable of running Windows applications on several POSIX-compliant operating systems, such as Linux, MacOS and BSD. Instead of simulating internal Windows logic like a virtual machine or emulator, Wine translates Windows API calls into POSIX calls on-the-fly, eliminating the performance and memory penalties of other methods and allowing you to cleanly integrate Windows applications into your desktop.*

**This project is NEITHER associated NOR affiliated in any way or form with the Wine project.**

## Prerequisites

| prerequisite | version |
| --- | --- |
| [CPython](https://www.python.org/) | 3.x (tested with 3.{7,8,9,10}) |
| [Wine](https://www.winehq.org/) | >= 6.x (tested with regular & [staging](https://wine-staging.com/)) - expected to be in the user's [`PATH`](https://en.wikipedia.org/wiki/PATH_(variable)) |

## Installation

| branch | status | installation | documentation |
| --- | --- | --- | --- |
| master (release) | [![build_master](https://github.com/pleiszenburg/wenv/actions/workflows/test.yaml/badge.svg?branch=master "Build Status: master / release")](https://github.com/pleiszenburg/wenv/tree/master) | `pip install wenv` | [![docs_master](https://readthedocs.org/projects/wenv/badge/?version=latest&style=flat-square "Documentation Status: master / release")](https://wenv.readthedocs.io/en/latest/) |
| develop | [![build_develop](https://github.com/pleiszenburg/wenv/actions/workflows/test.yaml/badge.svg?branch=develop "Build Status: development branch")](https://github.com/pleiszenburg/wenv/tree/develop) | `pip install git+https://github.com/pleiszenburg/wenv.git@develop` | [![docs_develop](https://readthedocs.org/projects/wenv/badge/?version=develop&style=flat-square "Documentation Status: development branch")](https://wenv.readthedocs.io/en/develop/) |

After installing the package with `pip`, you must initialize the *Wine Python environment* by running `wenv init`.

## Examples

Fire up a shell and try the following:

```bash
(env) user@comp:~> uname
Linux
(env) user@comp:~> python -m platform
Linux
(env) user@comp:~> wenv python -m platform
Windows
```

`wenv pip` works just like one would expect. Have a look at the output of `wenv help` for more commands and information. For use as a shebang, `wenv python` has an alias: One can write `#!/usr/bin/env _wenv_python` at the top of scripts.

``wenv python`` can also be used as a **Jupyter kernel**, side-by-side with a Unix-version of Python. Have a look at the [wenv-kernel project](https://github.com/pleiszenburg/wenv-kernel).

## Security

Just like Wine, `wenv` can run malicious Windows software on Unix. **Never, ever, run `wenv` with root / super users privileges!** For details, check the section on [security](https://wenv.readthedocs.io/en/stable/security.html) in the documentation.

## Need help?

See section on [Getting Help](https://wenv.readthedocs.io/en/latest/support.html) on `wenv`'s documentation.

## Bugs & Issues

See section on [Bugs and Issues](https://wenv.readthedocs.io/en/stable/bugs.html) on `wenv`'s documentation.

## Miscellaneous

- Full project documentation
    - at [Read the Docs](https://wenv.readthedocs.io/en/latest/)
    - at [`wenv` repository](https://github.com/pleiszenburg/wenv/blob/master/docs/source/index.rst)
- [Authors](https://github.com/pleiszenburg/wenv/blob/master/AUTHORS.md)
- [Change log (current)](https://github.com/pleiszenburg/wenv/blob/develop/CHANGES.md) (changes in development branch since last release)
- [Change log (past)](https://github.com/pleiszenburg/wenv/blob/master/CHANGES.md) (release history)
- [Contributing](https://github.com/pleiszenburg/wenv/blob/master/CONTRIBUTING.md) (**Contributions are highly welcomed!**)
- [FAQ](https://wenv.readthedocs.io/en/stable/faq.html)
- [License](https://github.com/pleiszenburg/wenv/blob/master/LICENSE) (**LGPL v2.1**)
- [Upstream issues](https://github.com/pleiszenburg/wenv/issues?q=is%3Aissue+is%3Aopen+label%3Aupstream) (relevant bugs in dependencies)
