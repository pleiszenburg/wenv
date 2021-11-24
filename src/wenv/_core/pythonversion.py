# -*- coding: utf-8 -*-

"""
WENV
Running Python on Wine
https://github.com/pleiszenburg/wenv

    src/wenv/_core/pythonversion.py: Parse and handle Python versions

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

from typing import Any, Union

try:
    from typing import NotImplementedType # re-introduced in Python 3.10
except ImportError:
    NotImplementedType = type(NotImplemented)

from .typeguard import typechecked

# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# CLASS
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++


@typechecked
class PythonVersion:
    """
    Parse, compare and export Python versions. Immutable.

    Args:
        arch : Build architecture. Can be ``win32``, ``win64`` or ``arm64``.
        major : Python major version, i.e. ``X`` from ``X.0.0``.
        minor : Python minor version, i.e. ``X`` from ``0.X.0``.
        maintenance : Python maintenance version, i.e. ``X`` from ``0.0.X``.
        build : Type of build, e.g. ``aX``, ``bX``, ``rcX``, etc. If left empty or set to ``stable``, the build is considered stable.
    """

    def __init__(self, arch: str, major: int, minor: int, maintenance: int, build: str = "stable"):

        if arch not in ("win32", "win64", "arm64"):
            raise ValueError("Unknown arch: " + arch)
        if major <= 2:
            raise ValueError("Only Python 3 and newer supported")

        self._arch = arch
        self._major, self._minor, self._maintenance = major, minor, maintenance
        self._build = "stable" if build == "" else build

    def __str__(self) -> str:
        """
        Converts version to string.
        """

        return "%d.%d.%d.%s" % (
            self._major,
            self._minor,
            self._maintenance,
            self._build,
        )

    def __repr__(self) -> str:
        """
        Converts version to interactive string representation.
        """

        return "<Python %d.%d.%d.%s (%s)>" % (
            self._major,
            self._minor,
            self._maintenance,
            self._build,
            self._arch,
        )

    def __eq__(self, other: Any) -> Union[bool, NotImplementedType]:
        """
        Equality operator.
        """

        if not isinstance(other, type(self)):
            return NotImplemented

        return self._as_sort() == other._as_sort()

    def __gt__(self, other: Any) -> Union[bool, NotImplementedType]:
        """
        Greater than operator.
        """

        if not isinstance(other, type(self)):
            return NotImplemented

        return self._as_sort() > other._as_sort()

    def __lt__(self, other: Any) -> Union[bool, NotImplementedType]:
        """
        Lesser than operator.
        """

        if not isinstance(other, type(self)):
            return NotImplemented

        return self._as_sort() < other._as_sort()

    def _as_sort(self) -> str:

        return "%04d-%04d-%04d-%s" % (
            self._major,
            self._minor,
            self._maintenance,
            self._build,
        )

    @property
    def arch(self) -> str:
        """
        Build architecture.
        """

        return self._arch

    @property
    def major(self) -> int:
        """
        Python major version.
        """

        return self._major

    @property
    def minor(self) -> int:
        """
        Python minor version.
        """

        return self._minor

    @property
    def maintenance(self) -> int:
        """
        Python maintenance version.
        """

        return self._maintenance

    @property
    def build(self) -> str:
        """
        Type of build.
        """

        return self._build

    def as_block(self) -> str:
        """
        Returns:
            "Block", i.e. combination of major and minor version as string.
        """

        return "%d%d" % (self._major, self._minor)

    def as_config(self) -> str:
        """
        Returns:
            String for use in configuration.
        """

        return str(self)

    def as_url(self) -> str:
        """
        Returns:
            Download URL for Windows Embedded Build ZIP file.
        """

        return (
            "https://www.python.org/ftp/python/%d.%d.%d/"
            % (self._major, self._minor, self._maintenance)
            + self.as_zipname()
        )

    def as_zipname(self) -> str:
        """
        Returns:
            Name of Windows Embedded Build ZIP file.
        """

        build = "" if self._build == "stable" else self._build
        arch = "amd64" if self._arch == "win64" else self._arch
        sub_tuple = (self._major, self._minor, self._maintenance, build, arch)

        if build.startswith("post"):
            return "python-%d.%d.%d.%s-embed-%s.zip" % sub_tuple
        else:
            return "python-%d.%d.%d%s-embed-%s.zip" % sub_tuple

    @classmethod
    def from_config(cls, arch: str, version: str):
        """
        Parses version from configuration value.

        Args:
            arch : Build architecture.
            version : Full version string, including type of build.
        """

        segments = version.split(".")
        if not len(segments) in (3, 4):
            raise ValueError("wrong number of version segments")
        if len(segments) == 3:
            segments.append("stable")
        if not all((segment.isnumeric() for segment in segments[:3])):
            raise ValueError("version segments are not numeric")
        segments = tuple([int(segment) for segment in segments[:3]] + [segments[3]])

        return cls(arch, *segments)

    @classmethod
    def from_zipname(cls, zip_name: str):
        """
        Parse version from Windows Embedded Build ZIP file name.

        Args:
            zip_name : Name of file
        """

        if not isinstance(zip_name, str):
            raise TypeError("zip_name must be str")

        fragments = zip_name.split("-")
        fragments.append(fragments[3].split(".")[1])
        fragments[3] = fragments[3].split(".")[0]

        if not fragments[0] == "python":
            raise ValueError('fagment[0] != "python"')
        if not fragments[2] == "embed":
            raise ValueError('fagment[2] != "embed"')
        if not fragments[3] in ("win32", "amd64", "arm64"):
            raise ValueError('fagment[3] not in in ("win32", "amd64", "arm64")')
        if not fragments[4] == "zip":
            raise ValueError('fagment[4] != "zip"')

        arch = "win64" if fragments[3] == "amd64" else fragments[3]
        release = [int(f) if f.isnumeric() else f for f in fragments[1].split(".")]

        if isinstance(release[2], str):
            if not len(release[2]) > 0:
                raise ValueError("broken maintenance/build fragment")
            pos = None
            for pos_idx, char in enumerate(release[2]):
                if not char.isdigit():
                    pos = pos_idx
                    break
            if pos is None:
                raise ValueError("maintenance fragment could not be identified")
            release.append(release[2][pos:])
            release[2] = release[2][:pos]
            if not release[2].isnumeric():
                raise ValueError("maintenance fragment not numeric")
            release[2] = int(release[2])

        if len(release) == 3:
            release.append("stable")
        if not len(release) == 4:
            raise ValueError(
                "release does not have 4 fragments (major,minor,maintenance,build)"
            )

        return cls(arch, *release)
