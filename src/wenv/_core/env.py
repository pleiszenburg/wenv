# -*- coding: utf-8 -*-

"""

WENV
Running Python on Wine
https://github.com/pleiszenburg/wenv

	src/wenv/_core/env.py: Managing a Wine-Python environment

	Copyright (C) 2017-2019 Sebastian M. Ernst <ernst@pleiszenburg.de>

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
import zipfile

from .config import config_class
from .const import c, COVERAGE_STARTUP, HELP_STR
from .source import download, PythonVersion

# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# HELPER ROUTINES
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

def _symlink(src, dest):

	if not os.path.lexists(dest):
		os.symlink(src, dest)

	if not os.path.exists(dest):
		raise OSError('"{LINK:s}" could not be created'.format(LINK = dest))
	if not os.path.islink(dest):
		raise OSError('"{LINK:s}" is not a symlink'.format(LINK = dest))
	if os.readlink(dest) != src:
		raise OSError('"{LINK:s}" points to the wrong source'.format(LINK = dest))

# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# WINE-PYTHON ENVIRONMENT CLASS
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

class env_class:

# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# INIT
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

	def __init__(self, parameter = None):

		# Get config
		if parameter is None:
			self._p = config_class()
		else:
			if not isinstance(parameter, dict):
				raise TypeError('parameter is not a dictionary')
			self._p = parameter

		# Init internal dicts
		self._init_dicts()

	def _init_dicts(self):

		# Init Wine cmd names
		self._wine_dict = {'win32': 'wine', 'win64': 'wine64'}

		# Init Python environment paths
		self._init_path_dict()
		# Init Python commands and scripts
		self._init_cmd_dict()
		# Init internal CLI commands
		self._init_cli_dict()
		# Init environment variables
		self._init_envvar_dict()

	def _init_path_dict(self):

		version_string = ''.join(self._p['pythonversion'].split('.')[0:2])

		# python standard library
		lib_path = os.path.join(self._p['pythonprefix'], 'Lib')
		# site-packages
		sitepackages_path = os.path.join(lib_path, 'site-packages')
		# python interpreter
		interpreter_path = os.path.join(self._p['pythonprefix'], 'python.exe')
		# scripts
		scripts_path = os.path.join(self._p['pythonprefix'], 'Scripts')
		# pip
		pip_path = os.path.join(scripts_path, 'pip.exe')
		# pytest
		pytest_path = os.path.join(scripts_path, 'pytest.exe')
		# coverage
		coverage_path = os.path.join(scripts_path, 'coverage.exe')
		# stdlib zip filename
		stdlibzip_path = os.path.join(self._p['pythonprefix'], 'python%s.zip' % version_string)
		# pth filename (library path)
		pth_path = os.path.join(self._p['pythonprefix'], 'python%s._pth' % version_string)

		self._path_dict = dict(
			lib = lib_path,
			sitepackages = sitepackages_path,
			scripts = scripts_path,
			interpreter = interpreter_path,
			pip = pip_path,
			pytest = pytest_path,
			coverage = coverage_path,
			stdlibzip = stdlibzip_path,
			pth = pth_path,
			)

	def _init_cmd_dict(self):

		out = {'python': self._path_dict['interpreter']} # TODO check!

		if not os.path.exists(self._path_dict['scripts']):
			self._cmd_dict = out
			return

		scripts = os.listdir(self._path_dict['scripts'])
		for script in scripts:
			if not script.lower().endswith('.exe'):
				continue
			out[script[:-4]] = os.path.join(self._path_dict['scripts'], script)

		self._cmd_dict = out

	def _init_cli_dict(self):

		self._cli_dict = {
			item[5:]: getattr(self, item)
			for item in dir(self)
			if item.startswith('_cli_') and hasattr(getattr(self, item), '__call__')
			}

	def _init_envvar_dict(self):

		self._envvar_dict = {k: os.environ[k] for k in os.environ.keys()} # HACK Required for Travis CI
		self._envvar_dict.update(dict(
			WINEARCH = self._p['arch'], # Architecture
			WINEPREFIX = self._p['wineprefix'], # Wine prefix / directory
			WINEDLLOVERRIDES = 'mscoree=d', # Disable MONO: https://unix.stackexchange.com/a/191609
			WINEDEBUG = self._p['winedebug'], # Wine debug level
			PYTHONHOME = self._p['pythonprefix'], # Python home for Wine Python (can be a Unix path)
			))

# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# WINE BUG #47766 / ZUGBRUECKE BUG #49
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

	def wine_47766_workaround(self):
		"""
		PathAllocCanonicalize treats path segments start with dots wrong.
		https://bugs.winehq.org/show_bug.cgi?id=47766
		"""

		is_clean = lambda path: not any([seg.startswith('.') for seg in path.split(os.path.sep)])

		pythonprefix = os.path.abspath(self._p['pythonprefix'])

		if pythonprefix != self._p['pythonprefix']:
			self._p['pythonprefix'] = pythonprefix
			self._init_dicts()

		if is_clean(self._p['pythonprefix']):
			return

		import tempfile, hashlib
		link_path = os.path.join(
			tempfile.gettempdir(),
			'wenv-' + hashlib.sha256(self._p['pythonprefix'].encode('utf-8')).hexdigest()[:8],
			)
		if not is_clean(link_path):
			raise OSError('unable to create clean link path: "{LINK:s}"'.format(LINK = link_path))

		if os.path.exists(self._p['pythonprefix']):
			_symlink(self._p['pythonprefix'], link_path)

		self._p['pythonprefix'] = link_path
		self._init_dicts()

	def wine_47766_workaround_uninstall(self):

		self.wine_47766_workaround()

		if os.path.lexists(self._p['pythonprefix']):
			os.unlink(self._p['pythonprefix'])

# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# ENSURE ENVIRONMENT
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

	def ensure(self):

		self.setup_wineprefix()
		self.setup_pythonprefix()
		self.wine_47766_workaround() # must run after setup_pythonprefix and before setup_pip
		self.setup_pip()

# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# DESTROY / UNINSTALL ENVIRONMENT
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

	def uninstall(self):

		# Does Wine prefix exist?
		if os.path.exists(self._p['wineprefix']):
			# Delete tree
			shutil.rmtree(self._p['wineprefix'])

		# Does Python prefix exist?
		if os.path.exists(self._p['pythonprefix']):
			# Delete tree
			shutil.rmtree(self._p['pythonprefix'])

		self.wine_47766_workaround_uninstall()

# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# CACHE INSTALLATION FILES LOCALLY
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

	def cache(self):

		version = PythonVersion.from_config(self._p['arch'], self._p['pythonversion'])

		os.makedirs(self._p['cache'], exist_ok = True)

		with open(os.path.join(self._p['cache'], version.as_zipname()), 'wb') as f:
			f.write(self._get_python(offline = False))
		with open(os.path.join(self._p['cache'], 'get-pip.py'), 'wb') as f:
			f.write(self._get_pip(offline = False))

		for package in ('pip', 'setuptools', 'wheel'):
			self.cache_package(package)

	def cache_package(self, name):

		os.makedirs(self._p['packages'], exist_ok = True)

		meta = json.loads(
			download('https://pypi.org/pypi/%s/json' % name, mode = 'binary').decode('utf-8')
			)

		for item in meta['urls']:
			with open(os.path.join(self._p['packages'], item['filename']), 'wb') as f:
				f.write(download(item['url'], mode = 'binary'))

# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# Fetch installer data
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

	def _get_python(self, offline = False):

		version = PythonVersion.from_config(self._p['arch'], self._p['pythonversion'])

		if offline:
			with open(os.path.join(self._p['cache'], version.as_zipname()), 'rb') as f:
				return f.read()
		else:
			return download(version.as_url(), mode = 'binary')

	def _get_pip(self, offline = False):

		if offline:
			with open(os.path.join(self._p['cache'], 'get-pip.py'), 'rb') as f:
				return f.read()
		else:
			return download('https://bootstrap.pypa.io/get-pip.py', mode = 'text').encode('utf-8')

# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# SETUP
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

	def setup_wineprefix(self, overwrite = False):

		if not isinstance(overwrite, bool):
			raise TypeError('overwrite is not a boolean')

		# Does it exist?
		if os.path.exists(self._p['wineprefix']):
			# Exit if overwrite flag is not set
			if not overwrite:
				return
			# Delete if overwrite is set
			shutil.rmtree(self._p['wineprefix'])

		os.makedirs(self._p['wineprefix']) # HACK Wine on Travis CI expects folder to exist

		# Start wine server into prepared environment
		envvar_dict = self._envvar_dict.copy()
		envvar_dict['DISPLAY'] = ''
		proc = subprocess.Popen(
			['wine', 'wineboot', '-i'],
			env = envvar_dict
			)
		proc.wait()
		if proc.returncode != 0:
			sys.exit(1)

	def setup_pythonprefix(self, overwrite = False):

		if not isinstance(overwrite, bool):
			raise TypeError('overwrite is not a boolean')

		# Is there a pre-existing Python installation with identical parameters?
		preexisting = os.path.isfile(self._path_dict['interpreter'])

		# Is there a preexisting installation and should it be overwritten?
		if preexisting and overwrite:
			# Delete folder
			shutil.rmtree(self._p['pythonprefix'])

		# Make sure the target directory exists
		if not os.path.exists(self._p['pythonprefix']):
			# Create folder
			os.makedirs(self._p['pythonprefix'])

		# Only do if Python is not there OR if should be overwritten
		if overwrite or not preexisting:

			# Generate in-memory file-like-object
			archive_zip = BytesIO()
			# Fetch Python zip file
			archive_zip.write(self._get_python(self._p['offline']))
			# Unpack from memory to disk
			with zipfile.ZipFile(archive_zip) as f:
				f.extractall(path = self._p['pythonprefix']) # Directory created if required

			# Unpack Python library from embedded zip on disk
			with zipfile.ZipFile(self._path_dict['stdlibzip'], 'r') as f:
				f.extractall(path = self._path_dict['lib']) # Directory created if required
			# Remove Python library zip from disk
			os.remove(self._path_dict['stdlibzip'])

			# HACK: Fix library path in pth-file (CPython >= 3.6)
			with open(self._path_dict['pth'], 'w') as f:
				f.write('Lib\n.\n\n# Uncomment to run site.main() automatically\nimport site\n')

		# Create site-packages folder if it does not exist
		if not os.path.exists(self._path_dict['sitepackages']):
			# Create folder
			os.makedirs(self._path_dict['sitepackages'])

	def setup_pip(self):

		# Exit if it exists
		if os.path.isfile(self._path_dict['pip']):
			return

		if self._p['offline']:
			proc_getpip = subprocess.Popen([
				'wenv', 'python',
				os.path.join(self._p['cache'], 'get-pip.py'),
				'--no-index', '--find-links=%s' % self._p['packages'],
				])
			proc_getpip.wait()
		else:
			getpip = self._get_pip(self._p['offline'])
			proc_getpip = subprocess.Popen(['wenv', 'python'], stdin = subprocess.PIPE)
			proc_getpip.communicate(input = getpip)

	def install_package(self, name, update = False):
		"""
		Thin wrapper for `wenv pip install`
		"""
		pass

	def install_requirements(self, requirements):
		"""
		Installs requirements provided as a string similar to a requirements.txt file
		"""
		pass

	def link_package(self, name):
		"""
		Link package from surrounding Unix environment to Wine environment
		"""
		pass

	def copy_package(self, name):
		"""
		Copy package from surrounding Unix environment to Wine environment (_issues_50_workaround)
		"""
		pass

		# # Package path in unix-python site-packages
		# unix_pkg_path = os.path.abspath(os.path.dirname(__file__))
		# # Package path in wine-python site-packages
		# wine_pkg_path = os.path.abspath(os.path.join(self._path_dict['sitepackages'], 'zugbruecke'))
		#
		# if not self._p['_issues_50_workaround']:
		# 	# Link zugbruecke package into wine-python site-packages
		# 	_symlink(unix_pkg_path, wine_pkg_path)
		# else:
		# 	if not os.path.exists(wine_pkg_path):
		# 		# Copy zugbruecke package into wine-python site-packages
		# 		shutil.copytree(unix_pkg_path, wine_pkg_path)
		#
		# # Egg path in unix-python site-packages
		# unix_egg_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'zugbruecke.egg-info'))
		# # Egg path in wine-python site-packages
		# wine_egg_path = os.path.abspath(os.path.join(self._path_dict['sitepackages'], 'zugbruecke.egg-info'))
		#
		# if not self._p['_issues_50_workaround']:
		# 	# Link zugbruecke egg into wine-python site-packages
		# 	_symlink(unix_egg_path, wine_egg_path)
		# else:
		# 	if not os.path.exists(wine_egg_path):
		# 		# Copy zugbruecke egg into wine-python site-packages
		# 		shutil.copytree(unix_egg_path, wine_egg_path)

	def setup_coverage_activate(self):

		# Ensure that coverage is started with the Python interpreter
		siteconfig_path = os.path.join(self._path_dict['sitepackages'], 'sitecustomize.py')
		siteconfig_cnt = ''
		if os.path.isfile(siteconfig_path):
			with open(siteconfig_path, 'r') as f:
				siteconfig_cnt = f.read()
			if COVERAGE_STARTUP in siteconfig_cnt:
				return
		with open(siteconfig_path, 'w') as f:
			f.write(siteconfig_cnt + '\n' + COVERAGE_STARTUP)

# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# CLI
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

	def _cli_init(self):
		"sets up an environment (including Wine prefix, Python interpreter, pip and pytest)"

		self.ensure()

	def _cli_init_coverage(self):
		"enables coverage analysis inside wenv"

		self.setup_coverage_activate()

	def _cli_cache(self):
		"fetches installation files and caches them for offline usage (Python, pip, setuptools, wheel)"

		self.cache()

	def _cli_clean(self):
		"removes current environment (including Wine prefix, Python interpreter and pip)"

		self.uninstall()

	def _cli_help(self):
		"prints this help text"

		def colorize(text):
			for color, key in (
				('GREEN', 'python'),
				('CYAN', 'pip'),
				('YELLOW', 'wheel'),
				('MAGENTA', 'pytest'),
				('MAGENTA', 'py.test'),
				):
				text = text.replace(key, c[color] + key + c['RESET'])
			return text

		sys.stdout.write(HELP_STR.format(
			CLIS = '\n'.join([
				'- wenv {CLI:s}: {HELP:s}'.format(
					CLI = key,
					HELP = self._cli_dict[key].__doc__,
					)
				for key in sorted(self._cli_dict.keys())
				]),
			SCRIPTS = colorize('\n'.join([
				'- wenv {SCRIPT:s}'.format(
					SCRIPT = key,
					)
				for key in sorted(self._cmd_dict.keys())
				]))
			))
		sys.stdout.flush()

	def cli(self):

		# No command passed
		if len(sys.argv) < 2:
			sys.stderr.write('There was no command passed.\n')
			sys.stderr.flush()
			sys.exit(1)

		# Separate command and arguments
		cmd, param = sys.argv[1], sys.argv[2:]

		# Allow -h and --help
		if cmd in ['-h', '--help']:
			cmd = 'help'

		# Special CLI command
		if cmd in self._cli_dict.keys():
			self._cli_dict[cmd]()
			sys.exit(0)

		# Command is unknown
		if cmd not in self._cmd_dict.keys():
			sys.stderr.write('Unknown command or script: "{CMD:s}"\n'.format(CMD = cmd))
			sys.stderr.flush()
			sys.exit(1)

		# Get Wine depending on arch
		wine = self._wine_dict[self._p['arch']]

		self.wine_47766_workaround()

		# Replace this process with Wine
		os.execvpe(
			wine,
			(wine, self._cmd_dict[cmd]) + tuple(param), # Python 3.4: No in-place unpacking of param
			self._envvar_dict
			)

	def shebang(self):
		"""Working around a lack of Unix specification ...
		https://stackoverflow.com/q/4303128/1672565
		https://unix.stackexchange.com/q/63979/28301
		https://lists.gnu.org/archive/html/bug-sh-utils/2002-04/msg00020.html
		"""

		if len(sys.argv) < 2:
			raise OSError('entry point meant to be used as a shebang but no file name was provided')

		# Get Wine depending on arch
		wine = self._wine_dict[self._p['arch']]

		self.wine_47766_workaround()

		# Replace this process with Wine
		os.execvpe(
			wine,
			(wine, self._cmd_dict['python'], sys.argv[1]),
			self._envvar_dict
			)

# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# CLI EXPORT
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

def cli():

	env_class().cli()

def shebang():

	env_class().shebang()
