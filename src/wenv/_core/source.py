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
	r = requests.get(down_url)
	assert r.ok
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
			line[9].isdigit(),
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

def parse_zip_name(zip_name):

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

	return (arch,) + tuple(release)
