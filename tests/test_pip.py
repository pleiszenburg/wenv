# -*- coding: utf-8 -*-

"""

WENV
Running Python on Wine
https://github.com/pleiszenburg/wenv

	tests/test_util.py: Testing pip

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

from .lib import get_context, run_process

from wenv import Env

import pytest

# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# TEST(s)
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

@pytest.mark.parametrize('arch', get_context())
def test_pip(arch):

	out, err, code = run_process(['wenv', 'pip', 'list'], env = {'WENV_ARCH': arch})

	assert code == 0
	assert len(err.strip()) == 0
	assert 'pip' in out
	assert 'setuptools' in out
	assert 'pytest' not in out

	out, err, code = run_process(
		['wenv', 'pip', 'install', 'pytest'],
		env = {'WENV_ARCH': arch}
		)

	assert code == 0
	assert len(err.strip()) == 0

	out, err, code = run_process(['wenv', 'pip', 'list'], env = {'WENV_ARCH': arch})

	assert code == 0
	assert len(err.strip()) == 0
	assert 'pip' in out
	assert 'setuptools' in out
	assert 'pytest' in out

@pytest.mark.parametrize('arch', get_context())
def test_pip_api(arch):

	env = Env(arch = arch)

	out, err, code = run_process(['wenv', 'pip', 'list'], env = {'WENV_ARCH': arch})

	assert code == 0
	assert len(err.strip()) == 0
	assert 'pip' in out
	assert 'setuptools' in out
	assert 'requests' not in out

	env.install_package('requests')

	out, err, code = run_process(['wenv', 'pip', 'list'], env = {'WENV_ARCH': arch})

	assert code == 0
	assert len(err.strip()) == 0
	assert 'pip' in out
	assert 'setuptools' in out
	assert 'requests' in out
