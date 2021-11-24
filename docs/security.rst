:github_url:

.. _security:

.. index::
	triple: root; super user; privileges

Security
========

.. warning::

	*wenv* must be used with **caution**.

Beware:

- **DO NOT** run untrusted code (or DLLs)!
- **DO NOT** run it with root / super users privileges!

The following problems also directly apply to *wenv*:

- *Wine* can in fact theoretically run (some) `Windows malware`_.
- **NEVER run Wine as root!** See `FAQ at WineHQ`_ for details.

.. _Windows malware: https://en.wikipedia.org/wiki/Wine_(software)#Security
.. _FAQ at WineHQ: https://wiki.winehq.org/FAQ#Should_I_run_Wine_as_root.3F

.. warning::

	*wenv* does not actively prohibit its use with root privileges.
