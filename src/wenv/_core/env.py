# -*- coding: utf-8 -*-

"""
WENV
Running Python on Wine
https://github.com/pleiszenburg/wenv

    src/wenv/_core/env.py: Managing a Wine-Python environment

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

import json
from io import BytesIO
import os
import shutil
import subprocess
import sys
from typing import Any, Dict, Generator, List
import zipfile

from .config import EnvConfig
from .const import c, COVERAGE_STARTUP, HELP_STR
from .paths import Paths
from .source import download
from .typeguard import typechecked

import wenv # HACK für version

# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# CLASS
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

@typechecked
class Env:
    """
    Represents one Wine Python environment. Mutable.

    args:
        kwargs : An arbitrary number of keyword arguments matching valid configuration options. In previous releases, the constructor expected one optional argument, ``parameter``. It should either be ``None`` or a dictionary. In the latter case, the dictionary may contain all valid configuration options. ``parameter`` can still be used but is deprecated.
    """

    # +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    # INIT
    # +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

    def __init__(self, **kwargs: Any):

        if "parameter" in kwargs.keys():  # legacy API
            if len(kwargs) > 1:
                raise ValueError(
                    'legacy API: only allows one parameter dict, named "parameter"'
                )
            kwargs = kwargs["parameter"]
            if kwargs is None:
                kwargs = dict()
            if not isinstance(kwargs, dict) and not isinstance(kwargs, EnvConfig):
                raise TypeError(
                    "legacy API: only allows one parameter, must be a dict or EnvConfig"
                )
            if not isinstance(kwargs, EnvConfig):
                kwargs = EnvConfig(**kwargs)
        else:
            kwargs = EnvConfig(**kwargs)

        self._p = kwargs
        self._cmd_dict = None
        self._cli_dict = None
        self._envvar_dict = None

        self._init_dicts()

    def _init_dicts(self):
        """
        Initialize core dictionaries. Function can also be used for re-initialization.
        """

        # Init Wine cmd names
        self._wine_dict = {
            "win32": self._p["wine_bin_win32"],
            "win64": self._p["wine_bin_win64"],
            "arm64": self._p["wine_bin_arm64"],
        }

        # Init Python environment paths
        self._path_dict = Paths(self._p["pythonprefix"], self._p["pythonversion"])
        # Init Python commands and scripts
        self._init_cmd_dict()
        # Init internal CLI commands
        self._init_cli_dict()
        # Init environment variables
        self._init_envvar_dict()

    def _init_cmd_dict(self):

        @typechecked
        def ls_exe(directory: str) -> Generator:
            if not os.path.isdir(directory):
                return
            for item in os.listdir(directory):
                if not item.lower().endswith(".exe"):
                    continue
                yield item[:-4], os.path.join(directory, item)

        self._cmd_dict = dict(ls_exe(self._path_dict["scripts"]))
        self._cmd_dict.update(dict(ls_exe(self._path_dict["pythonprefix"])))

    def _init_cli_dict(self):

        self._cli_dict = {
            item[5:]: getattr(self, item)
            for item in dir(self)
            if item.startswith("_cli_") and hasattr(getattr(self, item), "__call__")
        }

    def _init_envvar_dict(self):

        self._envvar_dict = os.environ.copy()
        self._envvar_dict.update(
            dict(
                WINEARCH=self._p["arch"],  # Architecture
                WINEPREFIX=self._p["wineprefix"],  # Wine prefix / directory
                WINEDLLOVERRIDES="mscoree=d",  # Disable MONO: https://unix.stackexchange.com/a/191609
                WINEDEBUG=self._p["winedebug"],  # Wine debug level
                PYTHONHOME=self._p[
                    "pythonprefix"
                ],  # Python home for Wine Python (can be a Unix path)
                VIRTUAL_ENV="",  # Reset Unix virtual env variable - wenv is "independent"
                PIP_NO_WARN_SCRIPT_LOCATION="0",  # pip will not warn that pythonprefix and scripts are not in PATH
            )
        )
        if self._p["wineinstallprefix"] not in (
            None,
            "",
        ):  # allow custom installations of Wine outside of PATH
            path = self._envvar_dict.get("PATH", "")
            self._envvar_dict["PATH"] = (
                os.path.join(self._p["wineinstallprefix"], "bin") + ":" + path
            )
            ld_library_path = self._envvar_dict.get("LD_LIBRARY_PATH", "")
            self._envvar_dict["LD_LIBRARY_PATH"] = ":".join(
                (
                    os.path.join(self._p["wineinstallprefix"], "lib"),
                    os.path.join(self._p["wineinstallprefix"], "lib64"),
                    ld_library_path,
                )
            )  # https://wiki.winehq.org/FAQ#Can_I_install_more_than_one_Wine_version_on_my_system.3F

    # +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    # WINE BUG #47766 / ZUGBRUECKE BUG #49
    # +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

    def wine_47766_workaround(self):
        """
        Due to `Wine bug #47766`_ (in ``PathAllocCanonicalize``), *Wine* crashes if **any** folder in the path to ``pythonprefix`` is hidden Unix-style (i.e. prefixed with a dot / ``.``). This workaround creates a symlink directly pointing to ``pythonprefix`` into ``/tmp``, which is (more or less) guaranteed to be visible. It is then used instead of the actual ``pythonprefix``.

        Run ``setup_wineprefix`` and ``setup_pythonprefix`` **before** calling ``wine_47766_workaround``. Any subsequent action such as installing or using ``pip`` must happen **after** calling ``wine_47766_workaround``.

        .. _Wine bug #47766: https://bugs.winehq.org/show_bug.cgi?id=47766
        """

        is_clean = lambda path: not any(
            [seg.startswith(".") for seg in path.split(os.path.sep)]
        )

        pythonprefix = os.path.abspath(self._p["pythonprefix"])

        if pythonprefix != self._p["pythonprefix"]:
            self._p["pythonprefix"] = pythonprefix
            self._init_dicts()

        if is_clean(self._p["pythonprefix"]):
            return

        import tempfile, hashlib

        link_path = os.path.join(
            tempfile.gettempdir(),
            "wenv-"
            + hashlib.sha256(self._p["pythonprefix"].encode("utf-8")).hexdigest()[:8],
        )
        if not is_clean(link_path):
            raise OSError(
                'unable to create clean link path: "{LINK:s}"'.format(LINK=link_path)
            )

        if os.path.exists(self._p["pythonprefix"]):
            Paths.symlink(self._p["pythonprefix"], link_path)

        self._p["pythonprefix"] = link_path
        self._init_dicts()

    def wine_47766_workaround_uninstall(self):
        """
        Reverts the `Wine bug #47766`_ workaround, i.e. it removes the symlink.
        """

        self.wine_47766_workaround()

        if os.path.lexists(self._p["pythonprefix"]):
            os.unlink(self._p["pythonprefix"])

    # +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    # ENSURE ENVIRONMENT
    # +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

    def ensure(self):
        """
        Equivalent to ``wenv init``. Intended to be used by 3rd-party packages which want to "ensure" that ``wenv`` has been initialized (i.e. *Python* and *pip* are present and working). ``ensure()`` calls the following methods:

            - :meth:`wenv.Env.setup_wineprefix`
            - :meth:`wenv.Env.setup_pythonprefix`
            - :meth:`wenv.Env.wine_47766_workaround`
            - :meth:`wenv.Env.setup_pip`
        """

        self.setup_wineprefix()
        self.setup_pythonprefix()
        self.wine_47766_workaround()  # must run after setup_pythonprefix and before setup_pip
        self.setup_pip()

    # +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    # DESTROY / UNINSTALL ENVIRONMENT
    # +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

    def uninstall(self):
        """
        Equivalent to ``wenv clean``. It removes the current Wine Python environment, i.e. Python interpreter, pip, setuptools, wheel and all installed packages.
        """

        # Does Wine prefix exist?
        if os.path.exists(self._p["wineprefix"]):
            # Delete tree
            shutil.rmtree(self._p["wineprefix"])

        # Does Python prefix exist?
        if os.path.exists(self._p["pythonprefix"]):
            # Delete tree
            shutil.rmtree(self._p["pythonprefix"])

        self.wine_47766_workaround_uninstall()

    # +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    # CACHE INSTALLATION FILES LOCALLY
    # +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

    def cache(self):
        """
        Equivalent to ``wenv cache``. It fetches installation files and caches them for offline usage, including the Python interpreter, pip, setuptools and wheel.
        """

        os.makedirs(self._p["cache"], exist_ok=True)

        with open(os.path.join(self._p["cache"], self._p["pythonversion"].as_zipname()), "wb") as f:
            f.write(self._get_python(offline=False))
        with open(os.path.join(self._p["cache"], "get-pip.py"), "wb") as f:
            f.write(self._get_pip(offline=False))

        for package in ("pip", "setuptools", "wheel"):
            self.cache_package(package)

    def cache_package(self, name: str):
        """
        Caches a specific package by nameself.

        Args:
            name : Name of PyPI package
        """

        os.makedirs(self._p["packages"], exist_ok=True)

        meta = json.loads(
            download("https://pypi.org/pypi/%s/json" % name, mode="binary").decode(
                "utf-8"
            )
        )

        for item in meta["urls"]:
            with open(os.path.join(self._p["packages"], item["filename"]), "wb") as f:
                f.write(download(item["url"], mode="binary"))

    # +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    # Fetch installer data
    # +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

    def _get_python(self, offline: bool = False) -> bytes:

        if offline:
            with open(os.path.join(self._p["cache"], self._p["pythonversion"].as_zipname()), "rb") as f:
                return f.read()
        else:
            return download(self._p["pythonversion"].as_url(), mode="binary")

    def _get_pip(self, offline: bool = False) -> bytes:

        if offline:
            with open(os.path.join(self._p["cache"], "get-pip.py"), "rb") as f:
                return f.read()
        else:
            return download("https://bootstrap.pypa.io/get-pip.py", mode="text").encode(
                "utf-8"
            )

    # +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    # SETUP
    # +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

    def setup_wineprefix(self, overwrite: bool = False):
        """
        Part of the initialization process, but can be triggered on its own if required. It creates a *Wine* prefix according to *wenv*'s configuration.

        Args:
            overwrite : If set to ``True``, a pre-existing *Wine* prefix is removed before a new one is created.
        """

        if not isinstance(overwrite, bool):
            raise TypeError("overwrite is not a boolean")

        # Does it exist?
        if os.path.exists(self._p["wineprefix"]):
            # Exit if overwrite flag is not set
            if not overwrite:
                return
            # Delete if overwrite is set
            shutil.rmtree(self._p["wineprefix"])

        os.makedirs(
            self._p["wineprefix"]
        )  # HACK Wine on Travis CI expects folder to exist

        # Start wine server into prepared environment
        envvar_dict = self._envvar_dict.copy()
        envvar_dict["DISPLAY"] = ""
        proc = subprocess.Popen(["wine", "wineboot", "-i"], env=envvar_dict)
        proc.wait()
        if proc.returncode != 0:
            sys.exit(1)

        self._init_dicts()

    def setup_pythonprefix(self, overwrite: bool = False):
        """
        Part of the initialization process, but can be triggered on its own if required. It installs the *CPython* interpreter into the *Python* prefix.

        Args:
            overwrite : If set to ``True``, a pre-existing *Python* prefix is removed before a new one is created.
        """

        if not isinstance(overwrite, bool):
            raise TypeError("overwrite is not a boolean")

        # Is there a pre-existing Python installation with identical parameters?
        preexisting = os.path.isfile(self._path_dict["interpreter"])

        # Is there a preexisting installation and should it be overwritten?
        if preexisting and overwrite:
            # Delete folder
            shutil.rmtree(self._p["pythonprefix"])

        # Make sure the target directory exists
        if not os.path.exists(self._p["pythonprefix"]):
            # Create folder
            os.makedirs(self._p["pythonprefix"])

        # Only do if Python is not there OR if should be overwritten
        if overwrite or not preexisting:

            # Generate in-memory file-like-object
            archive_zip = BytesIO()
            # Fetch Python zip file
            archive_zip.write(self._get_python(self._p["offline"]))
            # Unpack from memory to disk
            with zipfile.ZipFile(archive_zip) as f:
                f.extractall(
                    path=self._p["pythonprefix"]
                )  # Directory created if required

            # Unpack Python library from embedded zip on disk
            with zipfile.ZipFile(self._path_dict["libzip"], "r") as f:
                f.extractall(
                    path=self._path_dict["lib"]
                )  # Directory created if required
            # Remove Python library zip from disk
            os.remove(self._path_dict["libzip"])

            # HACK: Fix library path in pth-file (CPython >= 3.6)
            with open(self._path_dict["pth"], "w") as f:
                f.write(
                    "Lib\n.\n\n# Uncomment to run site.main() automatically\nimport site\n"
                )

        # Create site-packages folder if it does not exist
        if not os.path.exists(self._path_dict["sitepackages"]):
            # Create folder
            os.makedirs(self._path_dict["sitepackages"])

        self._init_dicts()

    def setup_pip(self):
        """
        Part of the initialization process, but can be triggered on its own if required. It installs ``pip``, assuming that both the ``wineprefix`` and ``pythonprefix`` are already present.
        """

        # Exit if it exists
        if os.path.isfile(self._path_dict["pip"]):
            return

        envvar_dict = {k: os.environ[k] for k in os.environ.keys()}
        envvar_dict.update(self._p.export_envvar_dict())

        if self._p["offline"]:
            proc = subprocess.Popen(
                [
                    "wenv",
                    "python",
                    os.path.join(self._p["cache"], "get-pip.py"),
                    "--no-index",
                    "--find-links=%s" % self._p["packages"],
                ],
                env=envvar_dict,
            )
            proc.wait()
        else:
            getpip = self._get_pip(self._p["offline"])
            proc = subprocess.Popen(
                ["wenv", "python"], stdin=subprocess.PIPE, env=envvar_dict
            )
            proc.communicate(input=getpip)

        self._init_dicts()

    def setup_coverage_activate(self):
        """
        Equivalent to ``wenv init_coverage``. It enables coverage analysis inside wenv.
        """

        # Ensure that coverage is started with the Python interpreter
        siteconfig_cnt = ""
        if os.path.isfile(self._path_dict["sitecustomize"]):
            with open(self._path_dict["sitecustomize"], "r") as f:
                siteconfig_cnt = f.read()
            if COVERAGE_STARTUP in siteconfig_cnt:
                return
        with open(self._path_dict["sitecustomize"], "w") as f:
            f.write(siteconfig_cnt + "\n" + COVERAGE_STARTUP)

    # +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    # PACKAGE MANAGEMENT
    # +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

    def install_package(self, name: str, update: bool = False):
        """
        Thin wrapper for ``wenv pip install {-U} {name}``. Installs and/or updates a package.

        Args:
            name : Name of PyPI package
            update : Update flag
        """

        if not isinstance(name, str):
            raise TypeError("name must be str")
        if len(name) == 0:
            raise ValueError("name must not be empty")
        if not isinstance(update, bool):
            raise TypeError("update must be bool")

        cmd = ["wenv", "pip", "install"]
        if update:
            cmd.append("-U")
        cmd.append(name)

        envvar_dict = {k: os.environ[k] for k in os.environ.keys()}
        envvar_dict.update(self._p.export_envvar_dict())

        proc = subprocess.Popen(
            cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=envvar_dict
        )
        outs, errs = proc.communicate()
        if proc.returncode != 0:
            raise SystemError('installing package "%s" failed' % name, outs, errs)

        self._init_dicts()

    def uninstall_package(self, name: str):
        """
        Thin wrapper for ``wenv pip uninstall -y {name}``. Removes a package.

        Args:
            name : Name of PyPI package
        """

        if not isinstance(name, str):
            raise TypeError("name must be str")
        if len(name) == 0:
            raise ValueError("name must not be empty")

        envvar_dict = {k: os.environ[k] for k in os.environ.keys()}
        envvar_dict.update(self._p.export_envvar_dict())

        proc = subprocess.Popen(
            ["wenv", "pip", "uninstall", "-y", name],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            env=envvar_dict,
        )
        outs, errs = proc.communicate()
        if proc.returncode != 0:
            raise SystemError('uninstalling package "%s" failed' % name, outs, errs)

        self._init_dicts()

    def list_packages(self) -> List[Dict[str, str]]:
        """
        Thin wrapper for ``wenv pip list --format json``.

        Returns:
            A list of dictionaries of format ``{"name": "Name of PyPI package ", "version": "package version"}``.
        """

        envvar_dict = {k: os.environ[k] for k in os.environ.keys()}
        envvar_dict.update(self._p.export_envvar_dict())

        proc = subprocess.Popen(
            ["wenv", "pip", "list", "--format", "json"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            env=envvar_dict,
        )
        outs, errs = proc.communicate()
        if proc.returncode != 0:
            raise SystemError("listing packages failed", outs, errs)

        return json.loads(outs.decode("utf-8"))

    # +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    # CLI
    # +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

    def _cli_init(self):
        "sets up an environment (Wine prefix, Python interpreter, pip, setuptools, wheel)"

        self.ensure()

    def _cli_init_coverage(self):
        "enables coverage analysis inside wenv"

        self.setup_coverage_activate()

    def _cli_cache(self):
        "fetches installation files and caches them for offline usage (Python interpreter, pip, setuptools, wheel)"

        self.cache()

    def _cli_clean(self):
        "removes current environment (Python interpreter, pip, setuptools, wheel, all installed packages)"

        self.uninstall()

    def _cli_help(self):
        "prints this help text"

        def colorize(text):
            for color, key in (
                ("GREEN", "python"),
                ("CYAN", "pip"),
                ("YELLOW", "wheel"),
                ("MAGENTA", "pytest"),
                ("MAGENTA", "py.test"),
            ):
                text = text.replace(key, c[color] + key + c["RESET"])
            return text

        scripts = colorize(
            "\n".join(
                [
                    "- wenv {SCRIPT:s}".format(
                        SCRIPT=key,
                    )
                    for key in sorted(self._cmd_dict.keys())
                ]
            )
        )
        if len(scripts) == 0:
            scripts = "(None)"

        sys.stdout.write(
            HELP_STR.format(
                VERSION=wenv.__version__,
                CLIS="\n".join(
                    [
                        "- wenv {CLI:s}: {HELP:s}".format(
                            CLI=key,
                            HELP=self._cli_dict[key].__doc__,
                        )
                        for key in sorted(self._cli_dict.keys())
                    ]
                ),
                SCRIPTS=scripts,
            )
        )
        sys.stdout.flush()

    def _cli_version(self):
        "shows wenv's version (also available as `--version`)"

        sys.stdout.write(wenv.__version__ + '\n')
        sys.stdout.flush()

    def cli(self):
        """
        Command line interface entry point. Equivalent to ``wenv [...]``. Looks for sub-commands and parameters in ``sys.argv``.
        """

        # No command passed
        if len(sys.argv) < 2:
            sys.stderr.write("There was no command passed.\n")
            sys.stderr.flush()
            sys.exit(1)

        # Separate command and arguments
        cmd, param = sys.argv[1], sys.argv[2:]

        # Allow -h and --help
        if cmd in ["-h", "--help"]:
            cmd = "help"

        # Version exposed
        if cmd == "--version":
            cmd = "version"

        # Special CLI command
        if cmd in self._cli_dict.keys():
            self._cli_dict[cmd]()
            sys.exit(0)

        # Command is unknown
        if cmd not in self._cmd_dict.keys():
            sys.stderr.write('Unknown command or script: "{CMD:s}"\n'.format(CMD=cmd))
            sys.stderr.flush()
            sys.exit(1)

        # Get Wine depending on arch
        wine = self._wine_dict[self._p["arch"]]

        self.wine_47766_workaround()

        # Replace this process with Wine
        os.execvpe(
            wine,
            (wine, self._cmd_dict[cmd])
            + tuple(param),  # Python 3.4: No in-place unpacking of param
            self._envvar_dict,
        )

    def shebang(self):
        """
        shebang entry point for Wine Python interpreter. Equivalent to ``_wenv_python [...]``. Does not look at ``sys.argv``. It only passes ``sys.argv[1]`` on to the Wine Python interpreter.

        This interface is working around a lack of Unix specification, see:

            - https://stackoverflow.com/q/4303128/1672565
            - https://unix.stackexchange.com/q/63979/28301
            - https://lists.gnu.org/archive/html/bug-sh-utils/2002-04/msg00020.html
        """

        if len(sys.argv) < 2:
            raise OSError(
                "entry point meant to be used as a shebang but no file name was provided"
            )

        # Get Wine depending on arch
        wine = self._wine_dict[self._p["arch"]]

        self.wine_47766_workaround()

        # Replace this process with Wine
        os.execvpe(
            wine, (wine, self._cmd_dict["python"], sys.argv[1]), self._envvar_dict
        )


# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# CLI EXPORT
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++


def cli():

    Env().cli()


def shebang():

    Env().shebang()
