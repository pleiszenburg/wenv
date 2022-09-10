:github_url:

.. image:: _static/logo.png
	:alt: wenv

wenv - Running Python on Wine
=============================

.. |build_master| image:: https://github.com/pleiszenburg/wenv/actions/workflows/test.yaml/badge.svg?branch=master
	:target: https://github.com/pleiszenburg/wenv/actions/workflows/test.yaml
	:alt: Test Status: master / release
.. |docs_master| image:: https://readthedocs.org/projects/wenv/badge/?version=latest&style=flat-square
	:target: https://wenv.readthedocs.io/en/latest/
	:alt: Documentation Status: master / release
.. |license| image:: https://img.shields.io/pypi/l/wenv.svg?style=flat-square
	:target: https://github.com/pleiszenburg/wenv/blob/master/LICENSE
	:alt: LGPL 2.1
.. |status| image:: https://img.shields.io/pypi/status/wenv.svg?style=flat-square
	:target: https://github.com/pleiszenburg/wenv/issues
	:alt: Project Development Status
.. |pypi_version| image:: https://img.shields.io/pypi/v/wenv.svg?style=flat-square
	:target: https://pypi.python.org/pypi/wenv
	:alt: pypi version
.. |pypi_versions| image:: https://img.shields.io/pypi/pyversions/wenv.svg?style=flat-square
	:target: https://pypi.python.org/pypi/wenv
	:alt: Available on PyPi - the Python Package Index
.. |chat| image:: https://img.shields.io/matrix/zugbruecke:matrix.org.svg?style=flat-square
	:target: https://matrix.to/#/#zugbruecke:matrix.org
	:alt: Matrix Chat Room
.. |mailing_list| image:: https://img.shields.io/badge/mailing%20list-groups.io-8cbcd1.svg?style=flat-square
	:target: https://groups.io/g/zugbruecke-dev
	:alt: Mailing List

|build_master| |docs_master| |license| |status| |pypi_version| |pypi_versions| |chat| |mailing_list|

User's guide
------------

*wenv* is a **Python package** (currently in development **status 4/beta**). It allows to **run Python on top of Wine** on Linux, MacOS or BSD. It handles required plumbing related to making Python and a number of Python modules work on Wine. `wenv` creates isolated virtual environments which can be transparently used from a Unix command line and which seamlessly integrate into Unix Python virtual environments.

.. toctree::
   :maxdepth: 2
   :caption: Introduction

   introduction
   installation
   examples

.. toctree::
   :maxdepth: 2
   :caption: Reference

   usage
   configuration
   api

.. toctree::
   :maxdepth: 2
   :caption: Advanced

   security
   bugs
   changes
   faq
   support

`Interested in contributing?`_

.. _Interested in contributing?: https://github.com/pleiszenburg/wenv/blob/master/CONTRIBUTING.md

Indices and tables
------------------

* :ref:`genindex`
* :ref:`search`
