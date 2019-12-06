# WENV
# Running Python on Wine
# https://github.com/pleiszenburg/wenv
#
#	makefile: GNU makefile for project management
#
# 	Copyright (C) 2017-2019 Sebastian M. Ernst <ernst@pleiszenburg.de>
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


clean:
	-rm -r build/*
	-rm -r dist/*
	coverage erase
	make clean_py
clean_py:
	find src/ tests/ -name '*.pyc' -exec rm -f {} +
	find src/ tests/ -name '*.pyo' -exec rm -f {} +
	find src/ tests/ -name '*~' -exec rm -f {} +
	find src/ tests/ -name '__pycache__' -exec rm -fr {} +

release_clean:
	make clean
	-rm -r src/*.egg-info

docu:
	@(cd docs; make clean; make html)

release:
	make release_clean
	python setup.py sdist bdist_wheel
	gpg --detach-sign -a dist/wenv*.whl
	gpg --detach-sign -a dist/wenv*.tar.gz

upload:
	for filename in $$(ls dist/*.tar.gz dist/*.whl) ; do \
		twine upload $$filename $$filename.asc ; \
	done

upload_test:
	for filename in $$(ls dist/*.tar.gz dist/*.whl) ; do \
		twine upload $$filename $$filename.asc -r pypitest ; \
	done

install:
	pip install -U -e .[dev]
	WENV_ARCH=win32 wenv init
	WENV_ARCH=win64 wenv init

test:
	make docu
	make test_quick

test_quick:
	make clean
	WENV_ARCH=win32 wenv python -m platform
	make clean_py
	WENV_ARCH=win64 wenv python -m platform
