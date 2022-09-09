# -*- coding: utf-8 -*-

"""
WENV
Running Python on Wine
https://github.com/pleiszenburg/wenv

    src/wenv/_core/source.py: Obtaining Python and pip locally or remotely

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

from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Optional, Union
from urllib.request import urlopen, Request

from .pythonversion import PythonVersion
from .typeguard import typechecked

# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# ROUTINES
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++


@typechecked
def download(down_url: str, mode: str = "binary") -> Union[str, bytes]:

    assert mode in ("text", "binary")
    assert isinstance(down_url, str)

    httprequest = Request(down_url)

    with urlopen(httprequest) as response:
        assert response.status == 200
        data = response.read()

    if mode == 'text':
        return data.decode('utf-8')

    return data # mode == 'binary'


@typechecked
def get_latest_python_build(
    arch: str,
    major: int,
    minor: int,
    builds: Optional[List[PythonVersion]] = None,
) -> Optional[PythonVersion]:
    """
    Find the latest build of a given Python major and minor version for a given architecture.
    Returns ``None`` if none can be found.

    Args:
        arch : Build architecture.
        major : Python major version.
        minor : Python minor version.
        builds : A list of :class:`wenv.PythonVersion` objects. If left empty, ``python.org`` will be queried.
    Returns:
        A :class:`wenv.PythonVersion` object or ``None``.
    """

    if builds is None:
        builds = get_available_python_builds()

    filtered_build = [
        build
        for build in builds
        if all((
            build.arch == arch,
            build.major == major,
            build.minor == minor,
        ))
    ]

    if len(filtered_build) == 0:
        return None

    filtered_build.sort()
    return filtered_build[-1]


@typechecked
def get_available_python_builds(parallel: int = 8) -> List[PythonVersion]:
    """
    Queries ``python.org`` for Windows Embedded Builds.

    Args:
        parallel : Number of parallel queries to ``python.org``.
    Returns:
        All available Windows Embedded Builds of CPython 3.
    """

    versions = [
        tuple(int(nr) for nr in line.split('"')[1][:-1].split("."))
        for line in download("https://www.python.org/ftp/python/", mode="text").split(
            "\n"
        )
        if all(
            (
                line.startswith('<a href="'),
                line[9:10].isdigit(),
                not line.startswith('<a href="2.'),
            )
        )
    ] # get URLs of all verions, dump Python 2

    version_urls = [
        "https://www.python.org/ftp/python/%d.%d.%d/" % version
        if len(version) == 3
        else "https://www.python.org/ftp/python/%d.%d/" % version
        for version in versions
    ] # some URLs in early Python 3.X releases are following  `major.minor` pattern

    with ThreadPoolExecutor(max_workers = parallel) as p:
        version_futures = [
            p.submit(
                lambda x: download(x, mode="text"), version_url
            ) for version_url in version_urls
        ] # get inventory of all maintenance version downloads
        version_downloads = [
            future.result()
            for future in as_completed(version_futures)
        ]

    return [
        PythonVersion.from_zipname(line.split('"')[1])
        for version, version_url, version_download in zip(
            versions, version_urls, version_downloads
        )
        for line in version_download.split("\n")
        if all(
            (
                line.startswith('<a href="'),
                "embed" in line,
                ".zip" in line,
                ".zip.asc" not in line,
            )
        )
    ]
