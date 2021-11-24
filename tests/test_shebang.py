# -*- coding: utf-8 -*-

"""
WENV
Running Python on Wine
https://github.com/pleiszenburg/wenv

    tests/test_shebang.py: Testing Python interpreter shebang alias

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


def test_without_shebang():

    out, err, code = run_process(["python", "tests/shebang.py"])

    assert code == 0
    assert no_errors_in(err)
    assert "Hello from Linux on x86_64!" == out.strip()


@pytest.mark.parametrize("arch,build", get_context())
def test_with_shebang(arch, build):

    out, err, code = run_process(
        ["./tests/shebang.py"], env={"WENV_ARCH": arch, "WENV_PYTHONVERSION": str(build)}
    )

    assert code == 0
    assert no_errors_in(err)
    if arch == 'win32':
        assert "Hello from Windows on x86!" == out.strip()
    else:
        assert "Hello from Windows on AMD64!" == out.strip()
