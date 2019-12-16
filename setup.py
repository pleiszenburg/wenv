# -*- coding: utf-8 -*-

"""

WENV
Running Python on Wine
https://github.com/pleiszenburg/wenv

	setup.py: Used for package distribution

	Copyright (C) 2017-2019 Sebastian M. Ernst <ernst@pleiszenburg.de>

<LICENSE_BLOCK>
The contents of this file are subject to the GNU Lesser General Public License
Version 2.1 ("LGPL" or "License"). You may not use this file except in
compliance with the License. You may obtain a copy of the License at
https://www.gnu.org/licenses/old-licenses/lgpl-2.1.txt
https://github.com/pleiszenburg/wenv/blob/master/LICENSE

Software distributed under the License is distributed on an "AS IS" basis,
WITHOUT WARRANTY OF ANY KIND, either express or implied. See the License for the
specific language governing rights and limitations under the License.
</LICENSE_BLOCK>

"""


# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# IMPORT
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

from setuptools import (
	find_packages,
	setup
	)
import os
from sys import platform


# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# SETUP
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++


# Bump version HERE!
_version_ = '0.2.0'


# List all versions of Python which are supported
confirmed_python_versions = [
	('Programming Language :: Python :: %s' % x)
	for x in '3.4 3.5 3.6 3.7 3.8'.split()
	]


# Fetch readme file
with open(os.path.join(os.path.dirname(__file__), 'README.md')) as f:
	long_description = f.read()


# Just in case someone is actually running this on Windows ...
if platform.startswith('win'):
	raise SystemExit('You are already running Windows. No need for this package!')


setup(
	name = 'wenv',
	packages = find_packages('src'),
	package_dir = {'': 'src'},
	version = _version_,
	description = 'Running Python on Wine',
	long_description = long_description,
	long_description_content_type = 'text/markdown',
	author = 'Sebastian M. Ernst',
	author_email = 'ernst@pleiszenburg.de',
	url = 'https://github.com/pleiszenburg/wenv',
	download_url = 'https://github.com/pleiszenburg/wenv/archive/v%s.tar.gz' % _version_,
	license = 'LGPLv2',
	keywords = ['wine', 'cross platform'],
	scripts = [],
	include_package_data = True,
	install_requires = [
		'requests'
		],
	extras_require = {
		'dev': [
			'pytest',
			'coverage',
			'pytest-cov',
			'python-language-server',
			'setuptools',
			'Sphinx',
			'sphinx_rtd_theme',
			'twine',
			'wheel'
			]
		},
	zip_safe = False,
	entry_points = {'console_scripts': [
		'wenv = wenv:cli',
		'_wenv_python = wenv:shebang'
		]},
	classifiers = [
		'Development Status :: 4 - Beta',
		'Intended Audience :: Developers',
		'Intended Audience :: Information Technology',
		'Intended Audience :: Science/Research',
		'Intended Audience :: System Administrators',
		'License :: OSI Approved :: GNU Lesser General Public License v2 (LGPLv2)',
		'Operating System :: MacOS',
		'Operating System :: POSIX :: BSD',
		'Operating System :: POSIX :: Linux',
		'Programming Language :: Python :: 3'
		] + confirmed_python_versions + [
		'Programming Language :: Python :: 3 :: Only',
		'Programming Language :: Python :: Implementation :: CPython',
		'Topic :: Scientific/Engineering',
		'Topic :: Software Development',
		'Topic :: System :: Operating System',
		'Topic :: System :: Operating System Kernels',
		'Topic :: Utilities'
		]
	)
