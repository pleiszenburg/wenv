# -*- coding: utf-8 -*-

"""
WENV
Running Python on Wine
https://github.com/pleiszenburg/wenv

    src/wenv/_core/config.py: Handles the modules configuration

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
import json
import site
import sys
from typing import Any, Dict, Optional

from .const import CONFIG_FN
from .errors import EnvConfigParserError
from .pythonversion import PythonVersion
from .typeguard import typechecked

# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# CONFIGURATION CLASS
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++


@typechecked
class EnvConfig(dict):
    """
    Wine Python environment configuration. Subclass of ``dict``.
    It holds default values and overwrites them with values found in configuration files and environment variables.
    Usually, one should not work with this class directly - unless an access to current configuration parameters is desired.

    Args:
        override : Specify custom values for configuration parameters via keyword arguments.
    """

    _KEYS = (
        "arch",
        "pythonversion",
        "wine_bin_win32",
        "wine_bin_win64",
        "wine_bin_arm64",
        "winedebug",
        "wineinstallprefix",
        "prefix",
        "wineprefix",
        "pythonprefix",
        "offline",
        "cache",
        "packages",
        "_issues_50_workaround",
    )

    def __init__(self, **override: Any):

        # Call parent constructur, just in case
        super().__init__()

        # Get config from files
        self.update(self._get_config_from_files())

        # Add override parameters
        if len(override) > 0:
            self.update(override)

        # Version type cleanup
        if not isinstance(self['pythonversion'], PythonVersion):
            self['pythonversion'] = PythonVersion.from_config(
                arch = self['arch'],
                version = self['pythonversion'],
            )

    def __getitem__(self, key: str) -> Any:
        """
        Returns values from the following sources in the following order:

        - Environment variables
        - Internal storage, i.e. changed in the dictionary or read from configuration files.
        - Default values.

        Args:
            key : Name of configuration value.
        Returns:
            Arbitrary configuration value.
        """

        env_var = "WENV_{NAME:s}".format(NAME=key.upper())
        if env_var in os.environ.keys():
            value = os.environ[env_var]
            if len(value) > 0:
                if key == "pythonversion":
                    return PythonVersion.from_config(self['arch'], value)
                if value.isnumeric():
                    return int(value)
                if value.strip().lower() in ("true", "false"):
                    return {"true": True, "false": False}[value.strip().lower()]
                return value

        if key in self.keys():
            return super().__getitem__(key)

        if key == "arch":
            return "win32"  # Define Wine & Wine-Python architecture
        if key == "pythonversion":
            return PythonVersion(self['arch'], 3, 7, 4, 'stable')  # Define Wine-Python version
        if key == "wine_bin_win32":
            return "wine"
        if key == "wine_bin_win64":
            return "wine64"
        if key == "wine_bin_arm64":
            return "wine"
        if key == "winedebug":
            return "-all"  # Wine debug output off
        if key == "wineinstallprefix":
            return None  # no custom Wine installation outside of PATH
        if key == "prefix":
            install_location = os.path.abspath(__file__)
            if install_location.startswith(
                site.USER_BASE
            ):  # Hacky way of looking for a user installation
                return site.USER_BASE
            return sys.prefix
        if key == "wineprefix":
            return os.path.join(self["prefix"], "share", "wenv", self["arch"])
        if key == "pythonprefix":
            return os.path.join(
                self["wineprefix"], "drive_c", "python-%s" % self["pythonversion"]
            )
        if key == "offline":
            return False
        if key == "cache":
            return os.path.join(self["prefix"], "share", "wenv", "cache")
        if key == "packages":
            return os.path.join(self["cache"], "packages")
        if key == "_issues_50_workaround":
            return False  # Workaround for zugbruecke issue #50 (symlinks ...)

        raise KeyError("not a valid configuration key", key)

    def export_dict(self) -> Dict[str, Any]:
        """
        Exports a dictionary.
        """

        return {field: self[field] for field in self._KEYS}

    def export_envvar_dict(self) -> Dict[str, str]:
        """
        Exports a dictionary which can passed to the OS as a set of environment variables for ``wenv`` itself.
        """

        return {
            "WENV_" + field.upper(): "" if field is None else str(self[field])
            for field in self._KEYS
        }

    def _get_config_from_files(self) -> Dict:

        base = {}

        # Look for config in the usual spots
        for fn in [
            "/etc/wenv",
            os.path.join("/etc", CONFIG_FN), # TODO deprecated
            os.path.join("/etc", CONFIG_FN[1:]),
            os.path.join(os.path.expanduser("~"), CONFIG_FN),
            os.environ.get("WENV"),
            os.path.join(os.environ.get("WENV"), CONFIG_FN)
            if os.environ.get("WENV") is not None
            else None,
            os.path.join(os.getcwd(), CONFIG_FN),
        ]:

            cnt = self._load_config_from_file(fn)

            if cnt is not None:
                base.update(cnt)

        return base

    def _load_config_from_file(self, try_path: Optional[str] = None) -> Optional[Dict[str, Any]]:

        # If there is a path ...
        if try_path is None:
            return

        # Is this a file?
        if not os.path.isfile(try_path):
            return

        # Read file
        try:
            with open(try_path, "r", encoding="utf-8") as f:
                cnt = f.read()
        except Exception as e:
            raise EnvConfigParserError(
                'Config file could not be read: "%s"' % try_path
            ) from e

        # Try to parse it
        try:
            cnt = json.loads(cnt)
        except Exception as e:
            raise EnvConfigParserError(
                'Config file could not be parsed: "%s"' % try_path
            ) from e

        # Ensure that config has the right format
        if not isinstance(cnt, dict):
            raise EnvConfigParserError('Config file is malformed: "%s"' % try_path)

        return cnt
