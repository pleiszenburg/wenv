:github_url:

.. _wineenv:

.. index::
	single: env python
	single: env pip
	single: env pytest
	single: env init
	triple: wine; python; environment
	module: wenv._core.env

API: class ``Env``
==================

``wenv`` can not only be used from the command line. It also offers an API through its ``Env`` class.

Constructor: ``Env(parameter = None)``
--------------------------------------

The constructor expects one optional argument, ``parameter``. It should either be ``None`` or a dictionary. In the latter case, the dictionary may contain all valid configuration options.

Method: ``ensure()``
--------------------

Equivalent of ``wenv init``. Intended to be used by 3rd-party packages which want to "ensure" that ``wenv`` has been initialized (i.e. *Python* and *pip* are present and working).

Method: ``wine_47766_workaround()``
-----------------------------------

Due to *Wine*'s bug #47766, *Wine* crashes if **any** folder in the path to ``pythonprefix`` is hidden Unix-style (i.e. prefixed with a dot / ``.``). This workaround creates a symlink directly pointing to ``pythonprefix`` into ``/tmp``, which is (more or less) guaranteed to be visible. It is then used instead of the actual ``pythonprefix``. ``setup_wineprefix`` and ``setup_pythonprefix`` will work without it. Any subsequent action such as installing ``pip`` will not work without it.

Method: ``setup_wineprefix(overwrite = False)``
-----------------------------------------------

Part of the initialization process, but can be triggered on its own if required. It creates a *Wine* prefix according to *wenv*'s configuration. If ``overwrite`` is set to ``True``, a pre-existing *Wine* prefix is removed before a new one is created.

Method: ``setup_pythonprefix(overwrite = False)``
-------------------------------------------------

Part of the initialization process, but can be triggered on its own if required. It installs the *CPython* interpreter into the *Python* prefix. If ``overwrite`` is set to ``True``, a pre-existing *Python* prefix is removed before a new one is created.

Method: ``setup_pip()``
-----------------------

Part of the initialization process, but can be triggered on its own if required. It installs ``pip``, assuming that both the ``wineprefix`` and ``pythonprefix`` are already present.

Method: ``shebang()``
---------------------

Shebang entry point.

Method: ``cli()``
-----------------

Command line interface entry point.

Method: ``uninstall()``
-----------------------

Equivalent of ``wenv clear``. Removes the current Wine Python environment.

Method: ``setup_coverage_activate()``
-------------------------------------

Equivalent of ``wenv init_coverage``. Activates coverage analysis throughout the Wine Python environment.
