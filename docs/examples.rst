:github_url:

.. _examples:

.. index::
	single: init
	single: python
	single: shebang
	single: pip

Examples
========

Fire up a shell and try the following:

.. code:: bash

	(env) user@comp:~> uname
	Linux
	(env) user@comp:~> python -m platform
	Linux
	(env) user@comp:~> wenv python -m platform
	Windows

``wenv pip`` works just like one would expect. Have a look at the output of ``wenv help`` for more commands and information. For use as a shebang, ``wenv python`` has an alias: One can write ``#!/usr/bin/env _wenv_python`` at the top of scripts.

``wenv python`` can also be used as a **Jupyter kernel**, side-by-side with a Unix-version of Python. Have a look at the `wenv-kernel project`_.

.. _wenv-kernel project: https://github.com/pleiszenburg/wenv-kernel
