
.PHONY: \
	help \
	test test-python test-perl \
	quick-test quick-test-perl quick-test-python \
	dev-deps-print dev-deps-install dev-deb-install dev-all-install \
	docs docs-clean servedocs \
	dist install lint \
	clean clean-build clean-pyc clean-test clean-tags clean-env

.DEFAULT_GOAL := help

#####
# user-facing vars
# intended to be overridden if desired

PERL = perl
PERL_PROVE = prove
PIP = python3 -m pip
PYLINT = pylint
PYTHON = python3
PYTEST = pytest

# set VERBOSE=1 (either here or at command line)
# to get bash -x
#VERBOSE=

# end vars
#####

#######
# vpath

VPATH = $(abs_mkfile_dir)

# evaluate this _once_
abs_mkfile_dir :=$(shell dirname $(realpath $(lastword $(MAKEFILE_LIST))))

#####
# detect OS

# plausible values: Windows, Darwin
ifeq ($(OS),Windows_NT)
    detected_OS := Windows
else
    detected_OS := $(shell sh -c 'uname 2>/dev/null || echo Unknown')
endif

####
# shell

ifeq ($(VERBOSE),1)
SHELL=bash -x
else
SHELL=bash
endif

#####
# inline python scripts

define print_help_pyscript
import re, sys

res=[]
for line in sys.stdin:
  match = re.match(r'^([a-zA-Z_-]+):.*?## (.*)$$', line)
  if match:
    target, help = match.groups()
    res.append( (target,help) )
res.sort()
for (target,help) in res:
    print("%-20s %s" % (target, help))
endef
export print_help_pyscript

# this Python fragment can be put in single quotes for
# use in bash
print_dev_deps_pyscript = import sys, os; sys.path.insert(0, "$(abs_mkfile_dir)"); import setup; test_deps=setup.setup_args["extras_require"]["test"]; print(" ".join(test_deps))

# this Python fragment can be put in single quotes for
# use in bash
print_doc_deps_pyscript = import sys, os; sys.path.insert(0, "$(abs_mkfile_dir)"); import setup; test_deps=setup.setup_args["extras_require"]["docs"]; print(" ".join(test_deps))

# end py scripts
#####

####
# virtual env definitions.

create_env = if [ ! -d env ] ; then python3 -m venv env; fi

ifeq ($(detected_OS),Windows)
ACTIVATE = ./env/Scripts/activate
else
ACTIVATE = ./env/bin/activate
endif

activate_env = if [ -z "$$VIRTUAL_ENV" ]; then . $(ACTIVATE); fi

create_tmpdir = $(PERL) -e 'use File::Temp "tempdir"; $$dir = tempdir("pytwine-tmp-XXXXXXXXXX", CLEANUP => 0, TMPDIR => 1 ); print $$dir;'

help: ## print targets
	@$(PYTHON) -c "$$print_help_pyscript" < $(MAKEFILE_LIST)

python_test_cmd = \
	$(PYTEST) \
		--color=yes \
		--html=./pytest_report.html --self-contained-html \
		--cov=pytwine \
		--cov-report term \
		--cov-report html \
		--doctest-modules -v \
			$(abs_mkfile_dir)/pytwine \
			$(abs_mkfile_dir)/tests

perl_test_cmd = $(PERL_PROVE) --verbose --comments $(abs_mkfile_dir)/t/*.t :: \
	--source-dir $(abs_mkfile_dir)


#######
# targets


help: ## print available targets
	@$(PYTHON) -c "$$print_help_pyscript" < $(MAKEFILE_LIST)

# except on windows, we don't bother
venv-init: ## create a venv if none already, install pip and wheel
	$(create_env)
	$(activate_env) && $(PIP) install --upgrade pip wheel

test: test-python test-perl ## run Perl and Python tests

test-python: ## run Python tests in a venv
	$(create_env)
	$(activate_env) && $(PIP) install -e "$(abs_mkfile_dir)[test]"
	$(activate_env) && $(PIP) install -e "$(abs_mkfile_dir)"
	$(activate_env) && $(python_test_cmd)

# if you are happy to run in working dir,
# and know all dependencies are installed:

quick-test: quick-test-python quick-test-perl ## run tests quickly with default interpreters

quick-test-python: ## run tests quickly with the default Python
	$(activate_env) && $(python_test_cmd)

# path to 'prove' does not seem to be found
# when using bash on Windows -- so use pwsh.
#
# also, virtual env and tmpdirs probably not
# worth the effort, so let `pip` install things globally.

# perl tests on Windows
ifeq ($(detected_OS),Windows)

test-perl: SHELL=pwsh.exe
test-perl:
	$(PIP) install -e "$(abs_mkfile_dir)[test]"
	$(PIP) install -e "$(abs_mkfile_dir)"
	$(perl_test_cmd)

quick-test-perl: SHELL=pwsh.exe
quick-test-perl:
	$(perl_test_cmd)

# perl tests on non-windows:
else

test-perl: ## run Perl-based tests from temp dir
	tmpdir=`$(create_tmpdir)`               && \
	cd $$tmpdir                             && \
	$(create_env)                           && \
	$(activate_env)                         && \
	$(PIP) install -e "$(abs_mkfile_dir)[test]" && \
	set -x && $(perl_test_cmd) || res=$$?   && \
	rm -rf $$tmpdir && set +x && exit $$res

quick-test-perl: ## run Perl-based tests quickly with the default interpreters
	$(activate_env) && $(perl_test_cmd)

# end perl tests
endif

# this variable only exists when something with 'dev' in the
# name is the goal.
ifeq ($(findstring dev,$(MAKECMDGOALS)),dev)
dev_deps := \
	$(shell python3 -c '$(print_dev_deps_pyscript)')
endif

dev-deps-print: ## print Python test dependencies
	@echo $(dev_deps)

dev-deps-install: ## install Python test dependencies
	$(PIP) install $(dev_deps)

dev-deb-install: ## install debian/ubuntu test dependencies
	sudo apt-get update
	sudo apt-get install libcarp-assert-perl

dev-all-install: dev-deb-install dev-deps-install ## install Python and debian/ubuntu test dependencies

## this variable only exists when something with 'doc' in the
## name is the goal.
#ifeq ($(findstring doc,$(MAKECMDGOALS)),doc)
#doc_deps := \
#	$(shell python3 -c '$(print_doc_deps_pyscript)')
#endif

docs: docs-clean ## generate Sphinx HTML documentation, including API docs
	$(create_env)
	$(activate_env) && $(PIP) install -e "$(abs_mkfile_dir)[docs]"
	$(activate_env) && $(MAKE) -C $(abs_mkfile_dir)/docs clean html

docs-clean: ## remove built documentation
	rm -rf $(abs_mkfile_dir)/docs/source/{_autosummary,pytwine.rst,modules.rst} \
		$(abs_mkfile_dir)/docs/build \
		$(abs_mkfile_dir)/docs/source/README.md

servedocs: docs ## compile the docs watching for changes
	watchmedo shell-command -p '*.rst' -c '$(MAKE) -C docs html' -R -D .

quick-docs:
	$(MAKE) -C $(abs_mkfile_dir)/docs html

dist: clean ## builds source and wheel package
	python setup.py sdist
	python setup.py bdist_wheel
	ls -l dist

install: clean ## install the package to the active Python's site-packages
	python3 setup.py install

lint/pylint: ## check style with pylint
	$(PYLINT) pytwine tests

lint: lint/pylint ## check style

clean: clean-build clean-pyc clean-test clean-tags ## remove all tagfile, build, test, coverage and Python artifacts

clean-build: ## remove build artifacts
	rm -rf   \
		build/ \
		dist/  \
		.eggs/
	find . -name '*.egg-info' -exec rm -fr {} +
	find . -name '*.egg' -exec rm -f {} +

clean-pyc: ## remove Python file artifacts
	find . \( -name '*.pyc' -o -name '*.pyo' \) -exec rm -f {} +
	find . \( -name '*~' -o -name '__pycache__' -o -name .mypy_cache \) -exec rm -rf {} +

clean-test: ## remove test and coverage artifacts
	rm -f .coverage
	rm -rf           \
		.tox/          \
		htmlcov/       \
		.hypothesis    \
		.pytest_cache

clean-env: ## remove 'env' dir
	rm -rf env

clean-tags: ## remove tagfiles
	rm -rf tags

