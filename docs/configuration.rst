:github_url:

.. _configuration:

.. index::
	pair: python; version
	triple: python; arch; architecture
	triple: wine; arch; architecture
	module: wenv._core.config

Configuration
=============

*wenv* can configure itself automatically or can be configured with files and environment variables manually.

Configuration files
-------------------

*wenv* uses ``JSON`` configuration files named ``.wenv.json``. They are expected in the following locations (in that order):

* The current working directory
* A directory specified in the ``WENV`` environment variable
* The user profile folder (``~`` / ``/home/{username}``)
* ``/etc``

There is one optional addition to the above rules: The path specified in the ``WENV`` environment variable can directly point to a configuration file. I.e. the ``WENV`` environment variable can also contain a path similar to ``/path/to/some/file.json``.

Configuration options are being looked for location after location in the above listed places. If, after checking for configuration files in all those locations, there are still configuration options left undefined, *wenv* will fill them with its defaults. A configuration option found in a location higher in the list will always be given priority over a the same configuration option with different content found in a location further down the list.

Configuration environment variables
-----------------------------------

Independently of the ``WENV`` environment variable, all configurable parameters of ``wenv`` can directly be overridden with environment variables. All values coming from configuration files will then be ignored for this particular parameter. Take the name of any configurable parameter, convert it to upper case and prefix it with ``WENV``. Example: The ``arch`` parameter can be overridden by declaring the ``WENV_ARCH`` environment variable.

Configurable parameters
-----------------------

``arch`` (str)
^^^^^^^^^^^^^^

Defines the architecture of *Wine* & *Wine* *Python*. It can be set to ``win32`` or ``win64``. Default is ``win32``, even on 64-bit systems. It appears to be a more stable configuration.

``pythonversion`` (str)
^^^^^^^^^^^^^^^^^^^^^^^

The ``pythonversion`` parameter tells *wenv* what version of the *Windows* *CPython* interpreter it should use. By default, it is set to ``3.7.4``.

Please note that 3.4 and earlier are not supported. In the opposite direction, at the time of writing, 3.6 (and later) do require *Wine* 4.0 or later. If you are forced to use *Wine* 2.0 or 3.0, you may try to set this parameter to ``3.5.4``. Note that you can only specify versions for which an "*Windows* embeddable zip file" is available, see `python.org`_.

.. _python.org: https://www.python.org/downloads/windows/

``prefix`` (str)
^^^^^^^^^^^^^^^^

If ``wenv`` is installed into a *Python* virtual environment or system-wide, this option's defaults is ``sys.prefix``. If ``wenv`` is installed user-wide, its default is ``site.USER_BASE`` (typically ``~/.local``).

``wineprefix`` (str)
^^^^^^^^^^^^^^^^^^^^

This parameter can be used to point to a custom ``WINEPREFIX`` outside of the ``shared`` folder of the current *Unix* *Python*'s prefix. By default, it is set to ``{prefix}/share/wenv/{arch}``

``pythonprefix`` (str)
^^^^^^^^^^^^^^^^^^^^^^

This parameter can be used to specify a custom location for the *Wine Python environment* outside of ``wineprefix`` if required. By default, it is set to ``{wineprefix}/drive_c/python-{pythonversion}/``

``winedebug`` (str)
^^^^^^^^^^^^^^^^^^^

*Wine* allows to control the level of debugging output through the ``WINEDEBUG`` environment variable. *wenv* will by default disable all output by setting it to ``-all``. A custom value can be specified in the ``winedebug`` configuration parameter. See the `Wine documentation`_ for details.

.. _Wine documentation: https://wiki.winehq.org/Debug_Channels

``offline`` (str/bool)
^^^^^^^^^^^^^^^^^^^^^^

If set to ``true``, ``wenv init`` will try to create a *Wine Python environment* from a locally cached *Windows Python* interpreter and a locally cached ``get-pip.py`` script. An exception is raised if any of the required components is not found in the local cache. For API usage, a boolean is expected. For command line usage / environment variables, strings equal to ``TRUE``/``True``/``true`` or ``FALSE``/``False``/``false`` are expected. By default, this option is set to ``false``.

``cache`` (str)
^^^^^^^^^^^^^^^

Path to the local cache directory. By default, it is set to ``{prefix}/share/wenv/cache``
