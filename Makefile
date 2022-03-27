
.PHONY: \
		test test-deps \
		perl-test python-test \
		docs \
		clean docs-clean

SHELL = bash
PYTEST = pytest
PERL_PROVE = prove
PIP = python3 -m pip

# evaluate this _once_
abs_mkfile_dir :=$(shell dirname $(realpath $(lastword $(MAKEFILE_LIST))))

create_env = if [ ! -e activate ]; then $(abs_mkfile_dir)/dev_env_init.sh $(abs_mkfile_dir); fi

activate_env = if [ -z "$$VIRTUAL_ENV" ]; then . ./activate; fi

# use like this:
# $(call create_tmpdir,testtype)
create_tmpdir=mktemp -d --tmpdir pytwine-$(1)-tmp-XXXXXXXXXX

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

python-test:
	$(create_env)
	$(activate_env) && \
		$(python_test_cmd)


perl_test_cmd = $(PERL_PROVE) --verbose --comments $(abs_mkfile_dir)/t/*.t :: \
		--source-dir $(abs_mkfile_dir)

perl-test:
		tmpdir=`$(call create_tmpdir,perltest)` && \
		cd $$tmpdir                             && \
		$(create_env)                           && \
		$(activate_env) &&  set -x && \
		$(perl_test_cmd) || res=$$? && \
		rm -rf $$tmpdir && set +x && exit $$res

test: python-test perl-test

# if you are happy to run in working dir,
# and know all dependencies are installed:
quick-test: quick-python-test quick-perl-test

quick-perl-test:
	$(perl_test_cmd)

quick-python-test:
	$(python_test_cmd)

test-deps:
	$(PIP) install `$(abs_mkfile_dir)/print_test_deps.py $(abs_mkfile_dir)`
	sudo apt-get update
	sudo apt-get install libcarp-assert-perl

docs:
	$(create_env)
	$(activate_env) && $(PIP) install -e "$(abs_mkfile_dir)[docs]" && \
		cd $(abs_mkfile_dir)/docs && \
		rm -rf source/_autosummary && \
		make clean html

quick-docs:
	cd $(abs_mkfile_dir)/docs && \
		make html

docs-clean:
	rm -rf $(abs_mkfile_dir)/docs/source/_autosummary \
		$(abs_mkfile_dir)/docs/build \
		$(abs_mkfile_dir)/docs/source/README.md

clean: docs-clean
	export GLOBIGNORE=".:.." && \
	topfiles=`ls -d $(abs_mkfile_dir)/* | grep -v -E 'env|git$$'` && \
	junk=`find $$topfiles \
	                -name '.hypothesis'     \
	             -o -name '__pycache__'     \
	             -o -name '*.egg-info'      \
	             -o -name '.pytest_cache'   \
	             -o -name '.coverage'       \
	             -o -name 'tags'            \
	             -o -name '.mypy_cache'`    \
	          && \
	rm -rf tags $$junk


