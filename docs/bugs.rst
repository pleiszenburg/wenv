:github_url:

.. _bugs:

.. index::
	triple: bug; issue; report
	triple: bug; issue; bisect
	single: wine

Bugs & Known Issues
===================

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

Known issue: ``OSError: [WinError 6] Invalid handle``
-----------------------------------------------------

On older versions of Linux such as *Ubuntu 14.04* alias *Trusty Tahr* (released 2014), you may observe errors when running ``wenv python``. Most commonly, they will present themselves as ``OSError: [WinError 6] Invalid handle: 'z:\\...`` triggered by calling ``os.listdir`` on a symbolic link ("symlink") to a folder.

.. note::

	A **clean solution** is to upgrade to a younger version of Linux. E.g. *Ubuntu 16.04* alias *Xenial Xerus* (released 2016) is known to work.

Known issue: SSL/TSL certificates outdated or broken
----------------------------------------------------

While running ``wenv init``, the command may terminate prematurely with an exception related to outdated or broken SSL/TSL certificates. This may happen on systems with older versions of ``libssl`` (``libopenssl``) or configuration issues regarding the SSL certificate store. You will most likely see additional information telling you that an SSL certificate could not be validated.

In most cases, a **clean solution** is to install ``certifi`` with pip: ``pip install -U certifi``. The ``-U`` option forces ``pip`` to update ``certifi`` if it is already installed. Once you have installed or updated ``certifi``, you can run ``wenv init`` again.
