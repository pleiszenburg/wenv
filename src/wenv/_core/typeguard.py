# -*- coding: utf-8 -*-

"""
WENV
Running Python on Wine
https://github.com/pleiszenburg/wenv

    src/wenv/_core/typeguard.py: Wrapper for typeguard for debugging

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
# WRAPPER
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

import os
import warnings

if os.environ.get('WENV_DEBUG', '0') == '1':
    from typeguard import typechecked
    warnings.warn("wenv running in debug mode with activated run-time type checks", RuntimeWarning)
else:
    typechecked = lambda x: x
