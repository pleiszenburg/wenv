:github_url:

.. _bugs:

.. index::
	triple: bug; issue; report
	triple: bug; issue; bisect
	single: wine

Bugs
====

Please report bugs in *wenv* in *wenv*'s `GitHub issue tracker`_.

Please report bugs in *Wine* in the `WineHQ Bug Tracking System`_.

Make sure to separate between *wenv*-related and *Wine*-related bugs.

.. _GitHub issue tracker: https://github.com/pleiszenburg/wenv/issues
.. _WineHQ Bug Tracking System: https://bugs.winehq.org/

How to bisect issues
--------------------

You can drop a configuration file named ``.wenv.json`` into your current working directory or your home folder (``/home/username``) and add configuration parameters to it, for example:

.. code:: javascript

	{"pythonversion": "3.8.0", "winedebug": "warn+all"}

If you are running into problems, the best approach usually is to try older versions of *Python* such as 3.7 or 3.6 first. Newer versions of *Python* use younger Windows APIs, which tend to cause more issues on Wine. If you change your *Python* version, you must initialize the new environment with ``wenv init``.

If you suspect that *Wine* is at fault, you can access *Wine* debug channels for more information by setting the ``winedebug`` option. See the `Wine documentation`_ for details.

For more *wenv* configuration options check the :ref:`chapter on configuration <configuration>`.

As an alternative approach, you can also investigate what happens if you run your code directly on *Windows*.

.. _Wine documentation: https://wiki.winehq.org/Debug_Channels
