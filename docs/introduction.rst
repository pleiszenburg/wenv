:github_url:

.. _introduction:

.. index::
	single: motivation
	single: implementation
	single: use cases

About ``wenv``
==============

.. _synopsis:

Synopsis
--------

*wenv* is a **Python package** (currently in development **status 4/beta**). It allows to **run Python on top of Wine** on Linux, MacOS or BSD. It handles required plumbing related to making Python and a number of Python modules work on Wine. `wenv` creates isolated virtual environments which can be transparently used from a Unix command line and which seamlessly integrate into Unix Python virtual environments.

.. _motivation:

Motivation
----------

*wenv* was derived from the Python package `zugbruecke`_. *zugbruecke* allows to call routines in *Windows* DLLs from *Python* code running on Unices / *Unix*-like systems such as *Linux*, *MacOS* or *BSD*. *wenv*'s code started out as infrastructure for *zugbruecke*. Eventually, it became too complex on its own and - at the same time - began to enable new and interesting use cases beyond the scope of *zugbruecke*.

Technically, the basic problem is how to install (and run) just any version or distribution of *Python* on *Wine*. The installers of most *Python* distributions including *Anaconda* and even *CPython* itself tend to be broken on most versions of *Wine* ("garbage" in *Wine* jargon). For a while, *ActiveState*'s *ActivePython* was the only "easy" way of directly installing *Python* on *Wine*, but even this path was (and still is) extremely unreliable. The commonly recommended workaround is to install *Python* directly on *Windows* and copy the resulting installation directory tree over to *Unix*/*Wine*. First, this is not an option for everybody as it requires a *Windows* installation. Second, it is also notoriously unreliable.

While researching options for developing *zugbruecke*, *CPython*'s `embeddable package`_ for *Windows* showed up on the radar. It is a simple ZIP-file without any installer. By merely unpacking it, one can run *Python* without an issue. With some manual tweaking and tuning of both the unpacked folder and *Wine*, it becomes possible to make ``pip`` work and install just about anything on top. *wenv* essentially takes care of the entire process automatically.

.. _zugbruecke: https://github.com/pleiszenburg/zugbruecke
.. _embeddable package: https://docs.python.org/3/using/windows.html#windows-embeddable

.. _implementation:

Implementation
--------------

*wenv* has two roles. First, it downloads, installs and configures both *CPython* and *pip*. The process is based on *CPython*'s embeddable package distribution for *Windows*. Second, *wenv* provides a thin launcher for starting *Python* (or just any *Python* application) on *Wine*. The installer and launcher themselves are also written in *Python* and run on any *Unix*-version of *Python*. The launcher sets the stage in *Unix Python* before using an `exec syscall`_ to replace itself with *Windows Python*.

.. _exec syscall: https://en.wikipedia.org/wiki/Exec_(system_call)

.. _usecases:

Use Cases
---------

- Running *Python* apps & scripts written for *Windows* on *Unix*.

- Running critical portions of *Python* apps depending on *Windows* on *Unix* - while the remaining uncritical portions of those apps can directly run on *Unix*. Inter-process communication can bridge the gap.

- Testing the *Windows* compatibility of *Python* apps directly on *Unix*.

- Accessing proprietary DLLs through ``ctypes``, ``cffi``, ``swig``, ``sip``, ``f2py`` and friends. Also see the `zugbruecke project`_.

- Running a *Windows* version of *Python* as a Jupyter kernel next to a *Unix* version, see the `wenv-kernel project`_.

.. _zugbruecke project: https://github.com/pleiszenburg/zugbruecke
.. _wenv-kernel project: https://github.com/pleiszenburg/wenv-kernel
