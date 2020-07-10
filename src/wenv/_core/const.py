# -*- coding: utf-8 -*-

"""

WENV
Running Python on Wine
https://github.com/pleiszenburg/wenv

	src/wenv/_core/const.py: Holds constant values, flags, types

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
# FOLDER- AND FILENAMES
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

CONFIG_FN = '.wenv.json'

# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# COVERAGE
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

COVERAGE_STARTUP = """
import coverage
coverage.process_startup()
"""

# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# CLI HELP
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

HELP_STR = """wenv - the Wine Python environment

{CLIS:s}

The following interpreters, scripts and modules are installed and available:

{SCRIPTS:s}
"""

# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# CLI COLORS
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

# https://en.wikipedia.org/wiki/ANSI_escape_code
c = {
	'RESET': '\033[0;0m',
	'BOLD': '\033[;1m',
	'REVERSE': '\033[;7m',
	'GREY': '\033[1;30m',
	'RED': '\033[1;31m',
	'GREEN': '\033[1;32m',
	'YELLOW': '\033[1;33m',
	'BLUE': '\033[1;34m',
	'MAGENTA': '\033[1;35m',
	'CYAN': '\033[1;36m',
	'WHITE': '\033[1;37m'
	}
