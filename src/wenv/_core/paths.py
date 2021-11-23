# -*- coding: utf-8 -*-

"""
WENV
Running Python on Wine
https://github.com/pleiszenburg/wenv

    src/wenv/_core/path.py: Wine-Python environment paths

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

from .pythonversion import PythonVersion
from .typeguard import typechecked

# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# PATHS
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++


@typechecked
class Paths:
    """
    Wine Python environment paths
    """

    def __init__(self, pythonprefix: str, pythonversion: PythonVersion):

        self._pythonprefix = pythonprefix
        self._pythonversion_block = pythonversion.as_block()

    def __getitem__(self, key: str) -> str:

        if key == "pythonprefix":
            return self._pythonprefix
        if key == "lib":
            return os.path.join(self["pythonprefix"], "Lib")
        if key == "sitepackages":
            return os.path.join(self["lib"], "site-packages")
        if key == "sitecustomize":
            return os.path.join(self["sitepackages"], "sitecustomize.py")
        if key == "scripts":
            return os.path.join(self["pythonprefix"], "Scripts")
        if key == "interpreter":
            return os.path.join(self["pythonprefix"], "python.exe")
        if key == "pip":
            return os.path.join(self["scripts"], "pip.exe")
        if key == "libzip":
            return os.path.join(
                self["pythonprefix"], "python%s.zip" % self._pythonversion_block
            )
        if key == "pth":
            return os.path.join(
                self["pythonprefix"], "python%s._pth" % self._pythonversion_block
            )

        raise KeyError("not a valid path key")

    @staticmethod
    def symlink(src, dest: str):
        """
        Generates a symlink and checks result
        """

        if not os.path.lexists(dest):
            os.symlink(src, dest)

        if not os.path.exists(dest):
            raise OSError('"{LINK:s}" could not be created'.format(LINK=dest))
        if not os.path.islink(dest):
            raise OSError('"{LINK:s}" is not a symlink'.format(LINK=dest))
        if os.readlink(dest) != src:
            raise OSError('"{LINK:s}" points to the wrong source'.format(LINK=dest))
