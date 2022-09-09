# WENV
# Running Python on Wine
# https://github.com/pleiszenburg/wenv
#
#	makefile: GNU makefile for project management
#
# 	Copyright (C) 2017-2022 Sebastian M. Ernst <ernst@pleiszenburg.de>
#
# <LICENSE_BLOCK>
# The contents of this file are subject to the GNU Lesser General Public License
# Version 2.1 ("LGPL" or "License"). You may not use this file except in
# compliance with the License. You may obtain a copy of the License at
# https://www.gnu.org/licenses/old-licenses/lgpl-2.1.txt
# https://github.com/pleiszenburg/wenv/blob/master/LICENSE
#
# Software distributed under the License is distributed on an "AS IS" basis,
# WITHOUT WARRANTY OF ANY KIND, either express or implied. See the License for the
# specific language governing rights and limitations under the License.
# </LICENSE_BLOCK>

# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# LIB
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

_clean_coverage:
	coverage erase

_clean_py:
	find src/ tests/ -name '*.pyc' -exec rm -f {} +
	find src/ tests/ -name '*.pyo' -exec rm -f {} +
	find src/ tests/ -name '*~' -exec rm -f {} +
	find src/ tests/ -name '__pycache__' -exec rm -fr {} +

_clean_release:
	-rm -r dist/*

# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# ENTRY POINTS
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

black:
	black .

clean:
	make _clean_release
	make _clean_coverage
	make _clean_py

docs:
	@(cd docs; make clean; make html)

install:
	pip install -U -e .[dev]
	# WENV_ARCH=win32 wenv init
	# WENV_ARCH=win64 wenv init

release:
	make clean
	flit build
	gpg --detach-sign -a dist/wenv*.whl
	gpg --detach-sign -a dist/wenv*.tar.gz

test:
	make clean
	WENV_DEBUG=1 pytest

upload:
	for filename in $$(ls dist/*.tar.gz dist/*.whl) ; do \
		twine upload $$filename $$filename.asc ; \
	done

.PHONY: docs
