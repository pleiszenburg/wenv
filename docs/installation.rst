:github_url:

.. _installation:

.. index::
	pair: pip; install
	triple: wine; linux; installation
	triple: wine; macos; installation
	triple: wine; bsd; installation

Installation
============

Getting *Wine*
--------------

For using *wenv*, you need to install **Wine** first. Depending on your platform, there are different ways of doing that.

* `Installation instructions for various Linux distributions`_
* `Installation instructions for Mac OS X`_
* `Installation instructions for FreeBSD`_

.. _Installation instructions for various Linux distributions: https://www.winehq.org/download
.. _Installation instructions for Mac OS X: https://wiki.winehq.org/MacOS
.. _Installation instructions for FreeBSD: https://wiki.winehq.org/FreeBSD

Currently, Wine >= 4.x is supported (tested). If you are limited to an older version of Wine such as 2.x or 3.x, you have one option: Try to set the ``pythonversion`` configuration parameter to ``3.5.4``.

Getting *wenv*
--------------

The latest  **stable release version** can be installed with *pip*:

.. code:: bash

	pip install wenv

If you are interested in testing the latest work from the **development branch**, you can try it like this:

.. code:: bash

	pip install git+https://github.com/pleiszenburg/wenv.git@develop

After installing the package with ``pip``, you must initialize the "Wine Python environment" by running ``wenv init``.

If you are relying on *wenv*, please notice that it uses semantic versioning. Breaking changes are indicated by increasing the first version number, the major version. Going for example from 0.0.x to 1.0.0 or going from 0.1.y to 1.0.0 therefore indicates a breaking change.

Possible problem: ``SSL/TSL has issues - please install "certifi" and try again``
---------------------------------------------------------------------------------

While running ``wenv init``, the command may terminate with a ``SystemExit`` exception entitled ``SSL/TSL has issues - please install "certifi" and try again``. This may happen on systems with older versions of ``libssl`` (``libopenssl``) or configuration issues regarding the SSL certificate store. You will most likely see additional information telling you that an SSL certificate could not be validated.

In most cases, a **clean solution** is to install ``certifi`` with pip: ``pip install -U certifi``. The ``-U`` option forces ``pip`` to update ``certifi`` if it is already installed. Once you have installed or updated ``certifi``, you can run ``wenv init`` again.

On known problematic systems, you may also choose to install ``wenv`` directly with ``certifi`` included: ``pip install wenv[certifi]``. Notice that this may have undesired security implications.

Possible problem: ``OSError: [WinError 6] Invalid handle``
----------------------------------------------------------

On older versions of Linux such as *Ubuntu 14.04* alias *Trusty Tahr* (released 2014), you may observe errors when running ``wenv python``. Most commonly, they will present themselves as ``OSError: [WinError 6] Invalid handle: 'z:\\...`` triggered by calling ``os.listdir`` on a symbolic link ("symlink") to a folder.

A **clean solution** is to upgrade to a younger version of Linux. E.g. *Ubuntu 16.04* alias *Xenial Xerus* (released 2016) is known to work.

Installing *wenv* in development mode
-------------------------------------

If you are interested in contributing to *wenv*, you might want to install it in development mode. You can find the latest instructions on how to do this in the `CONTRIBUTING file`_ of this project on *Github*.

.. _`CONTRIBUTING file`: https://github.com/pleiszenburg/wenv/blob/master/CONTRIBUTING.md
