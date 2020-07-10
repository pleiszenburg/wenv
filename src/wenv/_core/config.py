# -*- coding: utf-8 -*-

"""

WENV
Running Python on Wine
https://github.com/pleiszenburg/wenv

	src/wenv/_core/config.py: Handles the modules configuration

	Copyright (C) 2017-2020 Sebastian M. Ernst <ernst@pleiszenburg.de>

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

from .const import CONFIG_FN
from .errors import EnvConfigParserError

# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# CONFIGURATION CLASS
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

class EnvConfig(dict):

	def __init__(self, **override_dict):

		# Call parent constructur, just in case
		super().__init__()

		# Get config from files as a prioritized list
		for config in self._get_config_from_files():
			self.update(config)

		# Add override parameters
		if len(override_dict) > 0:
			self.update(override_dict)

	def __getitem__(self, key):

		env_var = 'WENV_{NAME:s}'.format(NAME = key.upper())
		if env_var in os.environ.keys():
			value = os.environ[env_var]
			if len(value) > 0:
				if value.isnumeric():
					return int(value)
				elif value.strip().lower() in ('true', 'false'):
					return {'true': True, 'false': False}[value.strip().lower()]
				else:
					return value

		if key in self.keys():
			return super().__getitem__(key)

		if key == 'arch':
			return 'win32' # Define Wine & Wine-Python architecture
		elif key == 'pythonversion':
			return '3.7.4' # Define Wine-Python version
		elif key == 'winedebug':
			return '-all' # Wine debug output off
		elif key == 'wineinstallprefix':
			return None # no custom Wine installation outside of PATH
		elif key == 'prefix':
			install_location = os.path.abspath(__file__)
			if install_location.startswith(site.USER_BASE): # Hacky way of looking for a user installation
				return site.USER_BASE
			else:
				return sys.prefix
		elif key == 'wineprefix':
			return os.path.join(self['prefix'], 'share', 'wenv', self['arch'])
		elif key == 'pythonprefix':
			return os.path.join(self['wineprefix'], 'drive_c', 'python-%s' % self['pythonversion'])
		elif key == 'offline':
			return False
		elif key == 'cache':
			return os.path.join(self['prefix'], 'share', 'wenv', 'cache')
		elif key == 'packages':
			return os.path.join(self['cache'], 'packages')
		elif key == '_issues_50_workaround':
			return False # Workaround for zugbruecke issue #50 (symlinks ...)
		else:
			raise KeyError('not a valid configuration key')

	def export_envvar_dict(self):

		return {
			'WENV_' + field.upper(): '' if field is None else str(self[field])
			for field in (
				'arch',
				'pythonversion',
				'winedebug',
				'wineinstallprefix',
				'prefix',
				'wineprefix',
				'pythonprefix',
				'offline',
				'cache',
				'packages',
				'_issues_50_workaround',
				)
			}

	def _get_config_from_files(self):

		# Look for config in the usual spots
		for fn in [
			'/etc/wenv',
			os.path.join('/etc', CONFIG_FN),
			os.path.join(os.path.expanduser('~'), CONFIG_FN),
			os.environ.get('WENV'),
			os.path.join(os.environ.get('WENV'), CONFIG_FN) if os.environ.get('WENV') is not None else None,
			os.path.join(os.getcwd(), CONFIG_FN),
			]:

			cnt_dict = self._load_config_from_file(fn)

			if cnt_dict is not None:
				yield cnt_dict

	def _load_config_from_file(self, try_path):

		# If there is a path ...
		if try_path is None:
			return

		# Is this a file?
		if not os.path.isfile(try_path):
			return

		# Read file
		try:
			with open(try_path, 'r', encoding = 'utf-8') as f:
				cnt = f.read()
		except:
			raise EnvConfigParserError('Config file could not be read: "%s"' % try_path)

		# Try to parse it
		try:
			cnt_dict = json.loads(cnt)
		except:
			raise EnvConfigParserError('Config file could not be parsed: "%s"' % try_path)

		# Ensure that config has the right format
		if not isinstance(cnt_dict, dict):
			raise EnvConfigParserError('Config file is malformed: "%s"' % try_path)

		return cnt_dict
