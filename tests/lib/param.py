# -*- coding: utf-8 -*-

"""
WENV
Running Python on Wine
https://github.com/pleiszenburg/wenv

    tests/lib/const.py: Holds constant values, flags, types

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

import os
import re
import signal
import subprocess

from .const import ARCHS, DEFAULT_TIMEOUT

from wenv import get_available_python_builds, get_latest_python_build

# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# BUILDS
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

_builds = get_available_python_builds()

BUILDS = {
    arch: [
        get_latest_python_build(arch, 3, minor, builds = _builds)
        for minor in range(
            7,  # min minor version
            10 + 1,  # max major version
        )
    ]
    for arch in ARCHS
}
for _value in BUILDS.values():
    _value.sort()

# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# ROUTINES
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++


def get_context():

    for arch in ARCHS:
        for build in BUILDS[arch]:
            yield arch, build


# https://stackoverflow.com/a/14693789/1672565
_ansi_escape_8bit = re.compile(br"(?:\x1B[@-_]|[\x80-\x9F])[0-?]*[ -/]*[@-~]")


def run_process(cmd_list, env=None, timeout=DEFAULT_TIMEOUT):

    if env is None:
        env = {}
    envvar_dict = os.environ.copy()
    envvar_dict.update(env)

    proc = subprocess.Popen(
        cmd_list, stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=envvar_dict
    )
    try:
        outs, errs = proc.communicate(timeout=timeout)
    except subprocess.TimeoutExpired:
        os.kill(proc.pid, signal.SIGINT)
        outs, errs = proc.communicate()

    return (
        _ansi_escape_8bit.sub(b"", outs).decode("utf-8"),
        errs.decode("utf-8"),
        proc.returncode,
    )
