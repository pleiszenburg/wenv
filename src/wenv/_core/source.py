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

import requests
import urllib.request

# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# PYTHON SSL FALLBACK
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

def download_old(_down_url):
	try:
		return urllib.request.urlopen(_down_url)
	except urllib.error.URLError as e:
		import ssl
		if not isinstance(e.args[0], ssl.SSLError):
			raise e # Not an SSL issue - this is unexpected ...
		try:
			_ = ModuleNotFoundError
			del _
		except NameError:
			ModuleNotFoundError = ImportError # Python 3.4 & 3.5
		try:
			import certifi
		except ModuleNotFoundError:
			raise SystemExit('SSL/TSL has issues - please install "certifi" and try again', e.args[0])
		return urllib.request.urlopen(_down_url, cafile = certifi.where())

# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# ROUTINES
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
