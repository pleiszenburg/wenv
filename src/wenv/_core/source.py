# -*- coding: utf-8 -*-

"""

WENV
Running Python on Wine
https://github.com/pleiszenburg/wenv

	src/wenv/_core/source.py: Obtaining Python and pip locally or remotely

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

from multiprocessing.pool import ThreadPool

import requests

# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# ROUTINES
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

def download(down_url, mode = 'binary'):

	assert mode in ('text', 'binary')
	assert isinstance(down_url, str)

	r = requests.get(down_url)

	assert r.ok
	r.raise_for_status()

	if r.encoding is not None:
		assert mode == 'text' and isinstance(r.text, str)
		return r.text
	else:
		assert mode == 'binary' and isinstance(r.content, bytes)
		return r.content

def get_available_python_versions():

	versions = [
		tuple(int(nr) for nr in line.split('"')[1][:-1].split('.'))
		for line in download('https://www.python.org/ftp/python/', mode = 'text').split('\n')
		if all([
			line.startswith('<a href="'),
			line[9:10].isdigit(),
			not line.startswith('<a href="2.')
			])
		]
	version_urls = [
		'https://www.python.org/ftp/python/%d.%d.%d/' % version
			if len(version) == 3 else
		'https://www.python.org/ftp/python/%d.%d/' % version
		for version in versions
		]
	version_downloads = ThreadPool(8).imap(lambda x: download(x, mode = 'text'), version_urls)
	embedded_versions = {
		version: {
			parse_zip_name(line.split('"')[1]): version_url + line.split('"')[1]
			for line in version_download.split('\n')
			if all((line.startswith('<a href="'), 'embed' in line, '.zip' in line, '.zip.asc' not in line))
			}
		for version, version_url, version_download in zip(versions, version_urls, version_downloads)
		}
	embedded_versions = {k: v for k, v in embedded_versions.items() if len(v) > 0}

	return embedded_versions

# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# CLASS: PYTHON VERSION
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

class python_version:

	def __init__(self, arch, major, minor, maintenance, build = 'stable'):

		if not isinstance(arch, str):
			raise TypeError('arch must be str')
		if arch not in ('win32', 'win64'):
			raise ValueError('Unknown arch: ' + arch)
		if any((not isinstance(item, int) for item in (major, minor, maintenance))):
			raise TypeError('Unknown type for major, minor or maintenance')
		if major <= 2:
			raise ValueError('Only Python 3 and newer supported')
		if not isinstance(build, str):
			raise TypeError('build must be str')

		self._arch = arch
		self._major, self._minor, self._maintenance = major, minor, maintenance
		self._build = 'stable' if build == '' else build

	def __str__(self):

		return '%d.%d.%d.%s' % (
			self._major, self._minor, self._maintenance, self._build
			)

	def __repr__(self):

		return '<Python %d.%d.%d.%s (%s)>' % (
			self._major, self._minor, self._maintenance, self._build, self._arch
			)

	@property
	def arch(self):

		return self._arch

	def as_url(self):

		build = '' if self._build == 'stable' else self._build
		arch = 'amd64' if self._arch == 'win64' else self._arch
		sub_tuple = (self._major, self._minor, self._maintenance, build, arch)

		if version[3].startswith('post'):
			filename = 'python-%d.%d.%d.%s-embed-%s.zip' % sub_tuple
		else:
			filename = 'python-%d.%d.%d%s-embed-%s.zip' % sub_tuple
		url = 'https://www.python.org/ftp/python/%d.%d.%d/' % sub_tuple[:3]

		return url + filename

	@classmethod
	def from_config(cls, arch, version):

		if not isinstance(version):
			raise TypeError('version must be str')
		segments = version.split('.')
		if not len(segments) in (3, 4):
			raise ValueError('wrong number of version segments')
		if len(segments) == 3:
			segments.append('stable')
		if not all((segment.isnumeric() for segment in segments[:3])):
			raise ValueError('version segments are not numeric')
		segments = tuple([int(segment) for segment in segments[:3]] + [segments[3]])

		return cls(arch, *segments)

	@classmethod
	def from_zipname(cls, zip_name):

		assert isinstance(zip_name, str)

		fragments = zip_name.split('-')
		fragments.append(fragments[3].split('.')[1])
		fragments[3] = fragments[3].split('.')[0]

		assert fragments[0] == 'python'
		assert fragments[2] == 'embed'
		assert fragments[3] in ('win32', 'amd64')
		assert fragments[4] == 'zip'

		arch = 'win32' if fragments[3] == 'win32' else 'win64'
		release = [
			int(f) if f.isnumeric() else f
			for f in fragments[1].split('.')
			]

		if isinstance(release[2], str):
			assert len(release[2]) > 0
			for pos, char in enumerate(release[2]):
				if not char.isdigit():
					break
			release.append(release[2][pos:])
			release[2] = release[2][:pos]
			assert release[2].isnumeric()
			release[2] = int(release[2])

		if len(release) == 3:
			release.append('stable')
		assert len(release) == 4

		return cls(arch, *release)
