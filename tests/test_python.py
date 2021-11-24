# -*- coding: utf-8 -*-

"""
WENV
Running Python on Wine
https://github.com/pleiszenburg/wenv

    tests/test_util.py: Testing Python interpreter

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

from .lib import get_context, run_process, no_errors_in

import pytest

# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# TEST(s)
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++


@pytest.mark.parametrize("arch,build", get_context())
def test_python(arch, build):

    out, err, code = run_process(
        ["wenv", "python", "-m", "platform"], env={"WENV_ARCH": arch, "WENV_PYTHONVERSION": str(build)}
    )

    assert code == 0
    assert no_errors_in(err)
    assert "Windows" in out

    out, err, code = run_process(
        ["wenv", "python", "-c", "import platform; print(platform.machine())"],
        env={"WENV_ARCH": arch, "WENV_PYTHONVERSION": str(build)},
    )
    assert code == 0
    assert no_errors_in(err)
    out = out.strip()
    assert (arch == "win32" and out == "x86") ^ (arch == "win64" and out == "AMD64")
