:github_url:

.. _examples:

.. index::
	single: init
	single: python
	single: shebang
	single: pip

Getting Started
===============

Fire up a shell. If you have not done so already, initialize a Wine Python environment first:

.. code:: bash

	(env) user@comp:~> wenv init

Now you can try the following:

.. code:: bash

	(env) user@comp:~> uname
	Linux
	(env) user@comp:~> python -m platform
	Linux
	(env) user@comp:~> wenv python -m platform
	Windows
	(env) user@comp:~> python --version
	Python 3.9.6
	(env) user@comp:~> wenv python --version
	Python 3.7.4

``wenv pip`` works just like one would expect:

.. code:: bash

	(env) user@comp:~> wenv pip list
	Package    Version
	---------- -------
	pip        21.3.1
	setuptools 59.2.0
	wheel      0.37.0
	(env) user@comp:~> wenv pip install requests
	Collecting requests
	  Downloading requests-2.26.0-py2.py3-none-any.whl (62 kB)
	     |████████████████████████████████| 62 kB 411 kB/s
	Collecting idna<4,>=2.5
	  Downloading idna-3.3-py3-none-any.whl (61 kB)
	     |████████████████████████████████| 61 kB 1.3 MB/s
	Collecting urllib3<1.27,>=1.21.1
	  Downloading urllib3-1.26.7-py2.py3-none-any.whl (138 kB)
	     |████████████████████████████████| 138 kB 1.9 MB/s
	Collecting certifi>=2017.4.17
	  Downloading certifi-2021.10.8-py2.py3-none-any.whl (149 kB)
	     |████████████████████████████████| 149 kB 2.5 MB/s
	Collecting charset-normalizer~=2.0.0
	  Downloading charset_normalizer-2.0.7-py3-none-any.whl (38 kB)
	Installing collected packages: urllib3, idna, charset-normalizer, certifi, requests
	Successfully installed certifi-2021.10.8 charset-normalizer-2.0.7 idna-3.3 requests-2.26.0 urllib3-1.26.7

Have a look at the output of ``wenv help`` for more commands and information:

.. code:: bash

	(env) user@comp:~> wenv help
	wenv - the Wine Python environment

	- wenv cache: fetches installation files and caches them for offline usage (Python interpreter, pip, setuptools, wheel)
	- wenv clean: removes current environment (Python interpreter, pip, setuptools, wheel, all installed packages)
	- wenv help: prints this help text
	- wenv init: sets up an environment (Wine prefix, Python interpreter, pip, setuptools, wheel)
	- wenv init_coverage: enables coverage analysis inside wenv

	The following interpreters, scripts and modules are installed and available:

	- wenv pip
	- wenv pip3
	- wenv pip3.7
	- wenv python
	- wenv pythonw
	- wenv wheel

If you install a package that includes new commands, they become available via ``wenv`` and will be shown in its help:

.. code:: bash

	(env) user@comp:~> wenv help | grep pytest
	(env) user@comp:~> wenv pip install pytest > /dev/null
	(env) user@comp:~> wenv help | grep pytest
	- wenv pytest
	(env) user@comp:~> wenv pytest --version
	pytest 6.2.5

The ``wenv python`` command behaves just like the regular ``python`` command on Unix:

.. code:: bash

	(env) user@comp:~> wenv python
	Python 3.7.4 (tags/v3.7.4:e09359112e, Jul  8 2019, 19:29:22) [MSC v.1916 32 bit (Intel)] on win32
	Type "help", "copyright", "credits" or "license" for more information.
	>>> import platform
	>>> platform.uname().system
	'Windows'
	>>> exit()
	(env) user@comp:~> wenv python -c "from platform import uname; print(uname().system)"
	Windows

Thanks to Wine, the **handling of paths** is seamless and transparent:

.. code:: bash

	(env) user@comp:~> python -c "import os; print(os.getcwd())"
	/home/user
	(env) user@comp:~> wenv python -c "import os; print(os.getcwd())"
	Z:\home\user

``wenv`` can be heavily configured via **configuration files and/or environment variables**. In the following example, two **Wine Python environments** are initialized. The first environment is using the ``wenv`` default Python version, 3.7.4. The second environment is using a custom Python version, 3.10.0:

.. code:: bash

	(env) user@comp:~> wenv init 2> /dev/null
	Collecting pip
	  Downloading pip-21.3.1-py3-none-any.whl (1.7 MB)
	     |################################| 1.7 MB 1.1 MB/s
	Collecting setuptools
	  Downloading setuptools-59.2.0-py3-none-any.whl (952 kB)
	     |################################| 952 kB 1.7 MB/s
	Collecting wheel
	  Downloading wheel-0.37.0-py2.py3-none-any.whl (35 kB)
	Installing collected packages: wheel, setuptools, pip
	Successfully installed pip-21.3.1 setuptools-59.2.0 wheel-0.37.0
	(env) user@comp:~> WENV_PYTHONVERSION=3.10.0 wenv init 2> /dev/null
	Collecting pip
	  Using cached pip-21.3.1-py3-none-any.whl (1.7 MB)
	Collecting setuptools
	  Using cached setuptools-59.2.0-py3-none-any.whl (952 kB)
	Collecting wheel
	  Using cached wheel-0.37.0-py2.py3-none-any.whl (35 kB)
	Installing collected packages: wheel, setuptools, pip
	Successfully installed pip-21.3.1 setuptools-59.2.0 wheel-0.37.0
	(env) user@comp:~> wenv python --version
	Python 3.7.4
	(env) user@comp:~> WENV_PYTHONVERSION=3.10.0 wenv python --version
	Python 3.10.0

.. note::

	*wenv* uses a somewhat unusual definition of "virtual environments" for its "Wine/Windows Python environments". *wenv* itself resides as a normal Python package within a regular Python virtual environment on the "Unix side". When ``wenv init`` is invoked, *wenv* will create a special kind of environment **underneath** the Unix Python virtual environment, by default in ``{prefix}/share/wenv/{arch}/drive_c/python-{pythonversion}/``. The parameters ``prefix``, ``arch`` and ``pythonversion`` can be :ref:`configured <configuration>`. The ``prefix`` parameter defaults to ``sys.prefix``, the root of the Unix Python environment. The location can also be overwritten as a whole by setting the ``pythonprefix`` parameter. In the above example, two "Wine Python environments" are created by altering the ``pythonversion`` parameter: The first one is based on the default ``pythonversion`` of 3.7.4, the second one is user-defined ``pythonversion`` of 3.10.0.

For use as a **shebang**, ``wenv python`` has an alias. One can write ``#!/usr/bin/env _wenv_python`` at the top of scripts:

.. code:: python

	#!/usr/bin/env _wenv_python

	import platform
	if __name__ == '__main__':
		print(f'Hello from {platform.uname().system:s}!')

If the above script was named ``hello_from_platform.py``, one could run it easily as follows:

.. code:: bash

	(env) user@comp:~> uname
	Linux
	(env) user@comp:~> chmod +x hello_from_platform.py
	(env) user@comp:~> ./hello_from_platform.py
	Hello from Windows!

``wenv python`` can also be used as a **Jupyter kernel**, side-by-side with a Unix-version of Python. Have a look at the `wenv-kernel project`_.

.. _wenv-kernel project: https://github.com/pleiszenburg/wenv-kernel
