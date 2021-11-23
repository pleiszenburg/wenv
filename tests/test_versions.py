# -*- coding: utf-8 -*-

"""
WENV
Running Python on Wine
https://github.com/pleiszenburg/wenv

    tests/test_versions.py: Test version parser and queries

    Copyright (C) 2017-2022 Sebastian M. Ernst <ernst@pleiszenburg.de>

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

from wenv import PythonVersion, get_available_python_builds, get_latest_python_build

# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# TEST(s)
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

def test_available_builds():

    builds = get_available_python_builds()

    assert len(builds) > 0
    assert all(isinstance(build, PythonVersion) for build in builds)

    for arch in ('win32', 'win64', 'arm64'):
        assert arch in (build.arch for build in builds)


def tests_latest_build():

    a = get_latest_python_build('win64', 3, 5)

    assert a == PythonVersion('win64', 3, 5, 4)


def test_stable_versions():

    a = PythonVersion('win64', 3, 9, 8, 'stable')
    b = PythonVersion('win64', 3, 10, 1, 'stable')

    assert a != b
    assert a < b
    assert b > a

def test_unstable_versions():

    a = PythonVersion('win64', 3, 9, 0, 'alpha')
    b = PythonVersion('win64', 3, 9, 0, 'rc1')

    assert a != b
    assert a < b
    assert b > a
