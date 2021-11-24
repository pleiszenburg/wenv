# -*- coding: utf-8 -*-

"""
WENV
Running Python on Wine
https://github.com/pleiszenburg/wenv

    tests/test_init.py: Testing clean & init

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

from .lib import get_context, run_process, no_errors_in, remove_colors

import pytest

# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# TEST(s)
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++


@pytest.mark.parametrize("arch,build", get_context())
def test_1_clean(arch, build):

    out, err, code = run_process(["wenv", "clean"], env={"WENV_ARCH": arch, "WENV_PYTHONVERSION": str(build)})

    assert code == 0
    assert no_errors_in(err)


@pytest.mark.parametrize("arch,build", get_context())
def test_2_init(arch, build):

    out, err, code = run_process(["wenv", "help"], env={"WENV_ARCH": arch, "WENV_PYTHONVERSION": str(build)})

    assert code == 0
    assert no_errors_in(err)
    assert "wenv pip" not in out
    assert 'wenv python' not in remove_colors(out)

    out, err, code = run_process(["wenv", "init"], env={"WENV_ARCH": arch, "WENV_PYTHONVERSION": str(build)})

    assert code == 0
    # assert len(err.strip()) == 0 # pip output goes to stderr

    out, err, code = run_process(["wenv", "help"], env={"WENV_ARCH": arch, "WENV_PYTHONVERSION": str(build)})

    assert code == 0
    assert no_errors_in(err)
    assert "wenv pip" in out
    assert 'wenv python' in remove_colors(out)


@pytest.mark.parametrize("arch,build", get_context())
def test_3_clean(arch, build):

    out, err, code = run_process(["wenv", "clean"], env={"WENV_ARCH": arch, "WENV_PYTHONVERSION": str(build)})

    assert code == 0
    assert no_errors_in(err)


@pytest.mark.parametrize("arch,build", get_context())
def test_4_offline(arch, build):

    out, err, code = run_process(["wenv", "help"], env={"WENV_ARCH": arch, "WENV_PYTHONVERSION": str(build)})

    assert code == 0
    assert no_errors_in(err)
    assert "wenv pip" not in out
    assert 'wenv python' not in remove_colors(out)

    out, err, code = run_process(["wenv", "cache"], env={"WENV_ARCH": arch, "WENV_PYTHONVERSION": str(build)})

    assert code == 0
    assert no_errors_in(err)
    assert "wenv pip" not in out

    out, err, code = run_process(
        ["wenv", "init"], env={"WENV_ARCH": arch, "WENV_PYTHONVERSION": str(build), "WENV_OFFLINE": "true"}
    )

    assert code == 0
    # assert len(err.strip()) == 0 # pip output goes to stderr

    out, err, code = run_process(["wenv", "help"], env={"WENV_ARCH": arch, "WENV_PYTHONVERSION": str(build)})

    assert code == 0
    assert no_errors_in(err)
    assert "wenv pip" in out
    assert 'wenv python' in remove_colors(out)
