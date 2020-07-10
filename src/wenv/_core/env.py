# -*- coding: utf-8 -*-

"""

WENV
Running Python on Wine
https://github.com/pleiszenburg/wenv

	src/wenv/_core/env.py: Managing a Wine-Python environment

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

import json
from io import BytesIO
import os
import shutil
import subprocess
import sys
import zipfile

from .config import EnvConfig
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
# PATHS
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

class Paths:

	def __init__(self, pythonprefix, arch, pythonversion):

		self._pythonprefix = pythonprefix
		self._pythonversion_block = PythonVersion.from_config(arch, pythonversion).as_block()

	def __getitem__(self, key):

		if key == 'pythonprefix':
			return self._pythonprefix
		elif key == 'lib':
			return os.path.join(self['pythonprefix'], 'Lib')
		elif key == 'sitepackages':
			return os.path.join(self['lib'], 'site-packages')
		elif key == 'sitecustomize':
			return os.path.join(self['sitepackages'], 'sitecustomize.py')
		elif key == 'scripts':
			return os.path.join(self['pythonprefix'], 'Scripts')
		elif key == 'interpreter':
			return os.path.join(self['pythonprefix'], 'python.exe')
		elif key == 'pip':
			return os.path.join(self['scripts'], 'pip.exe')
		elif key == 'libzip':
			return os.path.join(self['pythonprefix'], 'python%s.zip' % self._pythonversion_block)
		elif key == 'pth':
			return os.path.join(self['pythonprefix'], 'python%s._pth' % self._pythonversion_block)
		else:
			raise KeyError('not a valid path key')

# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# WINE-PYTHON ENVIRONMENT CLASS
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

class Env:

# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# INIT
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

	def __init__(self, **kwargs):

		if 'parameter' in kwargs.keys(): # legacy API
			if len(kwargs) > 1:
				raise ValueError('legacy API: only allows one parameter dict, named "parameter"')
			kwargs = kwargs['parameter']
			if kwargs is None:
				kwargs = dict()
			if not isinstance(kwargs, dict) and not isinstance(kwargs, EnvConfig):
				raise TypeError('legacy API: only allows one parameter, must be a dict or EnvConfig')
			if not isinstance(kwargs, EnvConfig):
				kwargs = EnvConfig(**kwargs)
		else:
			kwargs = EnvConfig(**kwargs)

		self._p = kwargs
		self._init_dicts()

	def _init_dicts(self):
		"""
		Initialize core dictionaries. Function can also be used for re-initialization.
		"""

		# Init Wine cmd names
		self._wine_dict = {'win32': 'wine', 'win64': 'wine64'}

		# Init Python environment paths
		self._path_dict = Paths(self._p['pythonprefix'], self._p['arch'], self._p['pythonversion'])
		# Init Python commands and scripts
		self._init_cmd_dict()
		# Init internal CLI commands
		self._init_cli_dict()
		# Init environment variables
		self._init_envvar_dict()

	def _init_cmd_dict(self):

		def ls_exe(dir):
			if not os.path.isdir(dir):
				return
			for item in os.listdir(dir):
				if not item.lower().endswith('.exe'):
					continue
				yield item[:-4], os.path.join(dir, item)

		self._cmd_dict = {
			item: path for item, path in ls_exe(self._path_dict['scripts'])
			}
		self._cmd_dict.update({
			item: path for item, path in ls_exe(self._path_dict['pythonprefix'])
			})

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
			VIRTUAL_ENV = '', # Reset Unix virtual env variable - wenv is "independent"
			PIP_NO_WARN_SCRIPT_LOCATION = '0', # pip will not warn that pythonprefix and scripts are not in PATH
			))
		if self._p['wineinstallprefix'] not in (None, ''): # allow custom installations of Wine outside of PATH
			path = self._envvar_dict.get('PATH', '')
			self._envvar_dict['PATH'] = os.path.join(self._p['wineinstallprefix'], 'bin') + ':' + path
			ld_library_path = self._envvar_dict.get('LD_LIBRARY_PATH', '')
			self._envvar_dict['LD_LIBRARY_PATH'] = ':'.join((
				os.path.join(self._p['wineinstallprefix'], 'lib'),
				os.path.join(self._p['wineinstallprefix'], 'lib64'),
				ld_library_path
				)) # https://wiki.winehq.org/FAQ#Can_I_install_more_than_one_Wine_version_on_my_system.3F

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
			with zipfile.ZipFile(self._path_dict['libzip'], 'r') as f:
				f.extractall(path = self._path_dict['lib']) # Directory created if required
			# Remove Python library zip from disk
			os.remove(self._path_dict['libzip'])

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

		envvar_dict = {k: os.environ[k] for k in os.environ.keys()}
		envvar_dict.update(self._p.export_envvar_dict())

		if self._p['offline']:
			proc = subprocess.Popen([
				'wenv', 'python',
				os.path.join(self._p['cache'], 'get-pip.py'),
				'--no-index', '--find-links=%s' % self._p['packages'],
				], env = envvar_dict
				)
			proc.wait()
		else:
			getpip = self._get_pip(self._p['offline'])
			proc = subprocess.Popen(
				['wenv', 'python'],
				stdin = subprocess.PIPE,
				env = envvar_dict
				)
			proc.communicate(input = getpip)

	def setup_coverage_activate(self):

		# Ensure that coverage is started with the Python interpreter
		siteconfig_cnt = ''
		if os.path.isfile(self._path_dict['sitecustomize']):
			with open(self._path_dict['sitecustomize'], 'r') as f:
				siteconfig_cnt = f.read()
			if COVERAGE_STARTUP in siteconfig_cnt:
				return
		with open(self._path_dict['sitecustomize'], 'w') as f:
			f.write(siteconfig_cnt + '\n' + COVERAGE_STARTUP)

# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# PACKAGE MANAGEMENT
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

	def install_package(self, name, update = False):
		"""
		Thin wrapper for `wenv pip install`
		"""

		if not isinstance(name, str):
			raise TypeError('name must be str')
		if len(name) == 0:
			raise ValueError('name must not be empty')
		if not isinstance(update, bool):
			raise TypeError('update must be bool')

		cmd = ['wenv', 'pip', 'install']
		if update:
			cmd.append('-U')
		cmd.append(name)

		envvar_dict = {k: os.environ[k] for k in os.environ.keys()}
		envvar_dict.update(self._p.export_envvar_dict())

		proc = subprocess.Popen(
			cmd,
			stdout = subprocess.PIPE, stderr = subprocess.PIPE,
			env = envvar_dict
			)
		outs, errs = proc.communicate()
		if proc.returncode != 0:
			raise SystemError('installing package "%s" failed' % name, outs, errs)

	def uninstall_package(self, name):
		"""
		Thin wrapper for `wenv pip uninstall -y`
		"""

		if not isinstance(name, str):
			raise TypeError('name must be str')
		if len(name) == 0:
			raise ValueError('name must not be empty')

		envvar_dict = {k: os.environ[k] for k in os.environ.keys()}
		envvar_dict.update(self._p.export_envvar_dict())

		proc = subprocess.Popen(
			['wenv', 'pip', 'uninstall', '-y', name],
			stdout = subprocess.PIPE, stderr = subprocess.PIPE,
			env = envvar_dict
			)
		outs, errs = proc.communicate()
		if proc.returncode != 0:
			raise SystemError('uninstalling package "%s" failed' % name, outs, errs)

	def list_packages(self):
		"""
		Thin wrapper for `wenv pip list --format json`
		"""

		envvar_dict = {k: os.environ[k] for k in os.environ.keys()}
		envvar_dict.update(self._p.export_envvar_dict())

		proc = subprocess.Popen(
			['wenv', 'pip', 'list', '--format', 'json'],
			stdout = subprocess.PIPE, stderr = subprocess.PIPE,
			env = envvar_dict
			)
		outs, errs = proc.communicate()
		if proc.returncode != 0:
			raise SystemError('uninstalling package "%s" failed' % name, outs, errs)

		return json.loads(outs.decode('utf-8'))

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

	Env().cli()

def shebang():

	Env().shebang()
