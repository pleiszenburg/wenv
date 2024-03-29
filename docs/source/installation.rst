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

.. note::

	Currently, Wine >= 6.x is supported (tested).

Getting *wenv*
--------------

The latest  **stable release version** can be installed with *pip*:

.. code:: bash

	pip install wenv

If you are interested in testing the latest work from the **development branch**, you can try it like this:

.. code:: bash

	pip install git+https://github.com/pleiszenburg/wenv.git@develop

After installing the package with ``pip``, you must **initialize** the "Wine Python environment" by running:

.. code:: bash

	wenv init

.. note::

	If you are relying on *wenv*, please notice that it uses **semantic versioning**. Breaking changes are indicated by increasing the second version number, the minor version. Going for example from 0.0.x to 0.1.y or going from 0.1.x to 0.2.y therefore indicates a breaking change.

If you are encountering any problems, see :ref:`section on bugs and known issues <bugs>`.

Installing *wenv* in Development Mode
-------------------------------------

If you are interested in contributing to *wenv*, you might want to install it in development mode. You can find the latest instructions on how to do this in the `CONTRIBUTING file`_ of this project on *Github*.

.. _`CONTRIBUTING file`: https://github.com/pleiszenburg/wenv/blob/master/CONTRIBUTING.md
